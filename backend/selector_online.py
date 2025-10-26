import os
import json
from typing import List, Dict, Any
import google.generativeai as genai
from tools_for_gemini import GEMINI_TOOLS, GEMINI_TOOL_FUNCS
from prompts import SYSTEM_POLICY_ETF_SELECTION

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY not set. Please export it to run fully online.")
genai.configure(api_key=GEMINI_KEY)

def _tool_runner(chat, part):
    """Execute a Gemini function call"""
    name = part.function_call.name
    args = dict(part.function_call.args or {})
    func = GEMINI_TOOL_FUNCS[name]
    result = func(args)
    return chat.send_message(
        genai.protos.FunctionResponse(name=name, response=result)
    )

def pick_etfs_for_sleeves(jurisdiction: str, sleeves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    sleeves: list from allocator.target_sleeves(); returns list of selections mapped to each non-cash sleeve.
    """
    # Build a compact request for Gemini
    need = [s for s in sleeves if s["class"] in ("equity","bonds","alts")]
    req = [{"class": s["class"], "subclass": s["subclass"], "jurisdiction": jurisdiction} for s in need]

    model = genai.GenerativeModel("models/gemini-1.5-pro")
    chat = model.start_chat(enable_automatic_function_calling=True, tools=GEMINI_TOOLS)

    # Seed policy + user request
    chat.send_message(SYSTEM_POLICY_ETF_SELECTION)
    resp = chat.send_message(
        "Select an ETF for each of these sleeves. Use tools to verify.\nREQUESTJSON:\n" + json.dumps(req)
    )

    # Handle function calls iteratively until final JSON
    for _ in range(15):  # safety bound
        done = True
        for part in resp.parts:
            if hasattr(part, "function_call"):
                done = False
                resp = _tool_runner(chat, part)
                break
        if done:
            break

    # Parse final response
    data = {}
    try:
        data = json.loads(resp.text)
    except Exception as e:
        raise RuntimeError(f"Gemini did not return valid JSON picks. Error: {e}\nRaw: {getattr(resp, 'text', '')}")

    if "picks" not in data or not isinstance(data["picks"], list):
        raise RuntimeError(f"Gemini picks malformed: {data}")

    # Return only for the sleeves we asked (skip CASH)
    out = []
    for s in need:
        pick = next((p for p in data["picks"] if p.get("subclass") == s["subclass"]), None)
        if not pick:
            raise RuntimeError(f"No ETF pick for subclass {s['subclass']}")
        out.append({
            "subclass": s["subclass"], 
            "symbol": pick["symbol"], 
            "name": pick.get("name",""), 
            "reasons": pick.get("reasons", []), 
            "expense_ratio": pick.get("expense_ratio")
        })
    return out
