<!-- Zoom Mode Debugging Steps -->

1. **Check if Bootstrap Icons loaded:**
   - Open browser dev tools (F12)
   - Look at the Network tab
   - Refresh the page
   - Check if "bootstrap-icons.css" loaded successfully

2. **Check console for JavaScript errors:**
   - Open browser dev tools (F12)
   - Look at Console tab
   - Check for any red error messages

3. **Verify the button exists in DOM:**
   - In dev tools, go to Elements tab
   - Search for "zoom-mode-toggle" (Ctrl+F)
   - You should find the button element

4. **Test button directly:**
   - In console, type: `document.getElementById('zoom-mode-toggle')`
   - Should return the button element (not null)

5. **Test the function:**
   - In console, type: `window.HUD.Zoom.toggleZoomMode()`
   - Should execute without error

6. **Check Bootstrap Icons CDN:**
   - Visit: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css
   - Should load the CSS file