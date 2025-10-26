# Growfolio Installation Instructions

Step-by-step guide to install and use the Growfolio Chrome extension.

## Prerequisites

- Google Chrome browser
- A computer running Windows, macOS, or Linux

## Step 1: Download the Extension

1. **Download the Frontend Folder**:
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract the ZIP file to a folder on your computer
   - Navigate to the `frontend` folder inside the extracted files

2. **Or clone just the frontend**:
   ```bash
   git clone https://github.com/your-username/Growfolio.git
   cd Growfolio/frontend
   ```

## Step 2: Verify Backend Connection (Optional)

The extension connects to a backend server hosted on Railway. The backend is already configured and running, so you don't need to set it up yourself.

**For development/testing purposes only**, if you want to run the backend locally:

## Step 3: Install the Chrome Extension

1. **Open Chrome Extensions Page**:
   - Open Google Chrome
   - Type `chrome://extensions/` in the address bar and press Enter
   - Or go to: Menu (☰) → Extensions → Manage Extensions

2. **Enable Developer Mode**:
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**:
   - Click "Load unpacked"
   - Navigate to the `frontend` folder you downloaded
   - Select the `frontend` folder
   - Click "Select Folder" (or "Open" on Mac)

4. **Verify Installation**:
   - You should see "Growfolio" appear in your extensions list
   - Look for the Growfolio icon in Chrome's toolbar

## Step 4: Start Using Growfolio

1. **Open the Extension**:
   - Click the Growfolio icon in your Chrome toolbar
   - Or use the puzzle piece icon to access pinned extensions

2. **Complete the Questionnaire**:
   - Fill out the 3-step financial profile
   - Answer questions about income, expenses, goals, and risk tolerance

3. **View Your Recommendations**:
   - Get instant AI-powered investment recommendations
   - See detailed explanations for each recommendation

4. **Export Your Analysis**:
   - Download your complete analysis as a TXT file
   - Share with a financial advisor if needed

## Troubleshooting

### Extension Not Loading?
- Make sure you selected the `frontend` folder (not the parent Growfolio folder)
- The `frontend` folder should contain `manifest.json`, `popup.html`, etc.
- Check that Developer mode is enabled
- Try reloading the extension (click the refresh icon on the extension card)

### Backend Connection Failed?
- The backend is hosted on Railway and should be accessible automatically
- If you see connection errors, check your internet connection
- The extension will automatically retry failed requests

### No Recommendations Showing?
- Complete all questionnaire steps before proceeding
- Check the browser console (F12) for any error messages
- Make sure you're connected to the internet

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the browser console for errors (F12)
3. Check the backend server logs
4. Open an issue on GitHub with details about the problem
