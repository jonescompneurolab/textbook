// ----------------------------------------
// Define page load ordering
// ----------------------------------------
function initSidebar() {
    const sidebar = document.getElementById("mySidebar");
    const savedState = localStorage.getItem("sidebarState");

    if (savedState === "closed") {
        sidebar.style.width = "0";
    } else {
        sidebar.style.width = maxWidth;
    }

    sidebar.style.visibility = "visible";
}

function initTopbar() {
    const topbar = document.querySelector(".topbar");
    const sidebarWidth = localStorage.getItem("sidebarState") === "closed" ? "0" : maxWidth;

    topbar.style.marginLeft = sidebarWidth;
    topbar.style.width = sidebarWidth === "0" ? "100%" : `calc(100% - ${sidebarWidth})`;
    topbar.style.visibility = "visible";
}

function initMainContent() {
    const main = document.getElementById("main");
    main.style.visibility = "visible";
}

function injectIframe() {
    const container = document.getElementById("video-container");
    if (container && container.dataset.src && !container.querySelector("iframe")) {
        const iframe = document.createElement("iframe");
        iframe.src = container.dataset.src;
        iframe.width = "640";
        iframe.height = "480";
        iframe.style.border = "none";
        iframe.style.display = "block";
        iframe.style.margin = "0 auto";
        iframe.allowFullscreen = true;
        container.appendChild(iframe);
    }
}

function hideIframes() {
    // Hide all iframes initially
    document.querySelectorAll('iframe').forEach(iframe => {
        iframe.style.visibility = 'hidden';
    });
}

function showIframes() {
    // Reveal all iframes after delay
    document.querySelectorAll('iframe').forEach(iframe => {
        iframe.style.visibility = 'visible';
    });
}

window.addEventListener("DOMContentLoaded", () => {
    initSidebar();
});

window.addEventListener("load", () => {
    initTopbar();
    initMainContent();
    hideIframes();
    injectIframe();

    setTimeout(() => {
        showIframes();
    }, 500);
});

// ----------------------------------------
// Manage footer
// ----------------------------------------
// This function will update the footer links when a page is loaded
// locally so that naivagation remains functional without a server
// Note: this solution is specific to MacOS

document.addEventListener("DOMContentLoaded", function() {
    if (window.location.protocol === "file:") {
        // Get the current local directory path
        const currentDir = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/'));

        // Process both previous and next links
        document.querySelectorAll('.previous-area, .next-area').forEach(function(area) {
            const link = area.getAttribute('data-link');
            
            if (link && link.startsWith("/")) {
                // Extract the local root directory
                const rootPath = currentDir.split("/textbook/")[0];
                // Prepend root path to link
                const resolvedLink = "file://" + rootPath + link;
                area.setAttribute("data-link", resolvedLink);
            }
        });
    }
});
// Hide the area if data-link is 'None'
document.querySelectorAll('.previous-area, .next-area').forEach(function(area) {
    if (area.getAttribute('data-link') === 'None') {
        area.style.display = 'none'; 
    }
});

// Redirect to the specified link
document.querySelectorAll('.previous-area, .next-area').forEach(function(area) {
    area.addEventListener('click', function() {
        window.location.href = area.getAttribute('data-link');
    });
});

// ----------------------------------------
// Manage sidebar
// ----------------------------------------
let isSidebarOpen = true; // Sidebar is initially open
let isSidebarFullyOpen = true; // Sidebar is fully open
const maxWidth = '350px';

function toggleNav() {
    const sidebar = document.getElementById("mySidebar");
    const main = document.getElementById("main");
    const topbar = document.querySelector(".topbar");

    // Toggle sidebar state
    if (isSidebarOpen) {
        sidebar.style.width = "0";
        main.style.marginLeft = "0";
        topbar.style.marginLeft = "0";
        topbar.style.width = "100%";
        isSidebarFullyOpen = false;
    } else {
        sidebar.style.width = maxWidth;
        main.style.marginLeft = maxWidth;
            // match margin to new width
        topbar.style.marginLeft = maxWidth;
        topbar.style.width = `calc(100% - ${maxWidth})`;
            // adjust topbar width
    }

    // Toggle the sidebar state
    isSidebarOpen = !isSidebarOpen;

    // Store the sidebar state in localStorage
    localStorage.setItem("sidebarState", isSidebarOpen ? "open" : "closed");
}

// Always listen for the transitionend on the sidebar
const sidebar = document.getElementById("mySidebar");
sidebar.addEventListener('transitionend', function() {
    if (sidebar.style.width === maxWidth) {
        // Sidebar has fully opened
        isSidebarFullyOpen = true;
    } else {
        // Sidebar is not fully open
        isSidebarFullyOpen = false;
    }
});

// add event listener to the sidebar close button
// that appears only on small screens
document.querySelector(".sidebar-close").addEventListener("click", toggleNav);

// Open the sidebar on page load
// -----------------------------

// Apply sidebar state before the page renders
// Added to help with initial page "flicker" as the position is
// calculated and applied
const savedState = localStorage.getItem("sidebarState");
if (savedState === "closed") {
    document.body.classList.add("sidebar-closed");
} else {
    document.body.classList.add("sidebar-open");
}

window.onload = function() {
    const sidebar = document.getElementById("mySidebar");
    const main = document.getElementById("main");
    const topbar = document.querySelector(".topbar");

    // Retrieve stored state
    const savedState = localStorage.getItem("sidebarState");

    // Determine initial state
    if (savedState === "closed") {
        sidebar.style.width = "0";
        main.style.marginLeft = "0";
        topbar.style.marginLeft = "0";
        topbar.style.width = "100%";
        isSidebarOpen = false;
        isSidebarFullyOpen = false;
    } else {
        sidebar.style.width = maxWidth;
        main.style.marginLeft = maxWidth;
        topbar.style.marginLeft = maxWidth;
        topbar.style.width = `calc(100% - ${maxWidth})`;
        isSidebarOpen = true;
        isSidebarFullyOpen = true;
    }

    // Disable transition for the initial state
    sidebar.style.transition = "none";
    main.style.transition = "none";
    topbar.style.transition = "none";

    // Re-enable transition for subsequent toggles
    setTimeout(() => {
        sidebar.style.transition = "width 0.5s";
        main.style.transition = "margin-left 0.5s";
        topbar.style.transition = "margin-left 0.5s, width 0.5s";
    }, 10);
}

function toggleSubmenu(event) {
    const header = event.target.closest('#sidebar-header');
        // Get the clicked header
    const submenu = header.nextElementSibling;
        // Get the submenu
    const toggleIcon = header.querySelector('.toggle-icon');
        // Get the icon

    if (submenu && submenu.classList.contains('submenu')) {
        submenu.classList.toggle('open'); 
            // Toggle the 'open' class to control visibility
        toggleIcon.textContent = submenu.classList.contains('open') ? '-' : '+'; 
            // Update icon
    }
}

// Resolve sidebar links for local development
// -------------------------------------------
// This function will update the sidebar links when a page is loaded
// locally so that sidebar naivagation remains functional without a server
// Note: this solution is specific to MacOS

document.addEventListener("DOMContentLoaded", function() {
    if (window.location.protocol === "file:") {
        // get the current local directory path
        const currentDir = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/'));

        // get 'absolute' links with root of 'textbook'
        const links = document.querySelectorAll("#mySidebar a");
        links.forEach(link => {
            const href = link.getAttribute("href");

            if (href && href.startsWith("/")) {
                // extract the local root directory
                const rootPath = currentDir.split("/textbook/")[0];
                // prepend root path to link
                const resolvedHref = "file://" + rootPath + href;
                link.setAttribute("href", resolvedHref);
            }
        });

        // Update image sources for icons
        const images = document.querySelectorAll(".social-icons img, .menu-icons img");
        images.forEach(img => {
            const src = img.getAttribute("src");

            if (src && src.startsWith("/")) {
                // extract the local root directory
                const rootPath = currentDir.split("/textbook/")[0];
                // prepend root path to image source
                const resolvedSrc = "file://" + rootPath + src;
                img.setAttribute("src", resolvedSrc);
            }
        });
    }
});

// Custom tooltips for the sidebar
// -------------------------------
// Flag to track tooltip visibility
let isTooltipVisible = false;
// Track pending tooltip timeout
let tooltipTimeoutId = null;

// Add text to the 'sidebar-tooltip' attribute for sidebar anchor tags
document.querySelectorAll('.sidebar a').forEach(anchor => {
    const cleanedText = anchor.textContent.replace(/[+\-]/g, '').trim();
    anchor.setAttribute('sidebar-tooltip', cleanedText);
});

// Handle sidebar tooltips
document.querySelectorAll('.sidebar a').forEach(function(link) {
    link.addEventListener('mouseenter', function(event) {
        const tooltipText = event.target.getAttribute('sidebar-tooltip');
        
        if (!tooltipText || isTooltipVisible || !isSidebarFullyOpen) return; // Only show tooltip if none is visible

        // Check if the text is overflowing
        if (event.target.scrollWidth > event.target.offsetWidth) {
            const delay = 500; // Set the delay time (in ms), adjust as needed

            // Create the tooltip after the delay
            tooltipTimeoutId = setTimeout(function() {
                // Remove any existing tooltips
                const existingTooltip = document.querySelector('.sidebar-tooltip');
                if (existingTooltip) {
                    existingTooltip.remove();
                }

                // Create the tooltip element dynamically
                const tooltip = document.createElement('div');
                tooltip.classList.add('sidebar-tooltip');  // Use the existing class
                tooltip.innerText = tooltipText;

                // Append the tooltip to the sidebar container
                const sidebarContainer = document.querySelector('.sidebar');
                sidebarContainer.appendChild(tooltip);

                // Get the position of the link and the sidebar container
                const rect = event.target.getBoundingClientRect();
                const sidebarRect = sidebarContainer.getBoundingClientRect();

                // Position the tooltip relative to the sidebar container
                tooltip.style.position = 'absolute';
                tooltip.style.left = `${rect.left - sidebarRect.left + sidebarContainer.scrollLeft + 20}px`;
                tooltip.style.top = `${rect.bottom - sidebarRect.top + sidebarContainer.scrollTop + 5}px`;

                // Make sure the tooltip is visible
                tooltip.style.opacity = '1';

                // Set the flag to true indicating that the tooltip is visible
                isTooltipVisible = true;

                // Reset the timeout id
                tooltipTimeoutId = null;
            }, delay); // Delay the tooltip creation
        }
    });

    link.addEventListener('mouseleave', function(event) {
        if (tooltipTimeoutId !== null) {
            clearTimeout(tooltipTimeoutId);
            tooltipTimeoutId = null;
        }

        // Remove the tooltip when the mouse leaves
        const tooltip = document.querySelector('.sidebar-tooltip');
        if (tooltip) {
            tooltip.remove();
        }

        // Reset the flag to false when the tooltip is removed
        isTooltipVisible = false;
    });
});

// Close all open submenus in the sidebar
// --------------------------------------
document.addEventListener("DOMContentLoaded", function() {
    // Function to close all open submenus in the navbar
    function closeAllSubmenus() {
        const allSubmenus = document.querySelectorAll('.submenu.open'); // Select all open submenus
        allSubmenus.forEach(submenu => {
            submenu.classList.remove('open'); // Remove 'open' class to collapse
            const toggleIcon = submenu.previousElementSibling.querySelector('.toggle-icon');
            if (toggleIcon) {
                toggleIcon.textContent = '+'; // Reset icon to '+'
            }
        });
    }

    // Add functionality to collapse button (SVG icon)
    const collapseIcon = document.querySelector('.collapse-icon');
    if (collapseIcon) {
        collapseIcon.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevent event propagation to avoid unwanted behavior
            closeAllSubmenus(); // Close all open submenus when the icon is clicked
        });
    }
});

// Keep the current page open in the sidebar
// -----------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    // Get the full path relative to the 'content' folder
    const currentPage = window.location.pathname.split("/content/")[1].split("?")[0];

    // Find the active link using the full path
    const activeLink = document.querySelector(`#mySidebar a[href$='${currentPage}']`);

    if (activeLink) {
        // Apply the active class
        activeLink.classList.add("active");
            // Find the closest submenu
        const submenu = activeLink.closest('.submenu');

        if (submenu) {
            // Keep the submenu open
            submenu.classList.add('open');
            const toggleIcon = submenu.previousElementSibling.querySelector('.toggle-icon');

            if (toggleIcon) {
                // Ensure the toggle icon reflects the open state
                toggleIcon.textContent = '-';
            }
        }
    }
});

// ------------------------------
// Font size buttons and dropdown
// ------------------------------
document.addEventListener("DOMContentLoaded", function() {
    const content = document.getElementById("content");

    // Retrieve and apply the saved font size
    const savedFontSize = localStorage.getItem("fontSize");
    if (savedFontSize && content) {
        content.style.fontSize = savedFontSize + "px";
    }
});

function increaseFontSize() {
    event.stopPropagation();  // Prevent dropdown from closing
    const content = document.getElementById("content");
    const currentSize = parseFloat(window.getComputedStyle(content).fontSize);
    const newSize = currentSize + 1;

    content.style.fontSize = newSize + "px";

    // save font size to localStorage
    localStorage.setItem("fontSize", newSize);
}

function decreaseFontSize() {
    event.stopPropagation();  // Prevent dropdown from closing
    const content = document.getElementById("content");
    const currentSize = parseFloat(window.getComputedStyle(content).fontSize);
    const newSize = currentSize - 1;

    content.style.fontSize = newSize + "px";

    // save font size to localStorage
    localStorage.setItem("fontSize", newSize);
}

// Dropdown for font buttons
function toggleDropdown() {
    const dropdownContent = document.querySelector('.dropdown-content');
    dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
}

// Open/close dropdown on click of the button
document.getElementById('dropdownButton').onclick = function(event) {
    event.stopPropagation();  // Prevent the click from triggering the window.onclick event
    toggleDropdown();
};

// Close dropdown if clicking outside
window.onclick = function(event) {
    const dropdownContent = document.querySelector('.dropdown-content');
    if (!event.target.closest('.dropdown')) {  // Close if click outside the dropdown
        dropdownContent.style.display = 'none';
    }
};

// ----------------------------------------
// Toggle between light and dark themes
// ----------------------------------------
// Wait for the DOM to be fully loaded

document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sunSVG = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
            <path d="M361.5 1.2c5 2.1 8.6 6.6 9.6 11.9L391 121l107.9 19.8c5.3 1 9.8 4.6 11.9 9.6s1.5 10.7-1.6 15.2L446.9 256l62.3 90.3c3.1 4.5 3.7 10.2 1.6 15.2s-6.6 8.6-11.9 9.6L391 391 371.1 498.9c-1 5.3-4.6 9.8-9.6 11.9s-10.7 1.5-15.2-1.6L256 446.9l-90.3 62.3c-4.5 3.1-10.2 3.7-15.2 1.6s-8.6-6.6-9.6-11.9L121 391 13.1 371.1c-5.3-1-9.8-4.6-11.9-9.6s-1.5-10.7 1.6-15.2L65.1 256 2.8 165.7c-3.1-4.5-3.7-10.2-1.6-15.2s6.6-8.6 11.9-9.6L121 121 140.9 13.1c1-5.3 4.6-9.8 9.6-11.9s10.7-1.5 15.2 1.6L256 65.1 346.3 2.8c4.5-3.1 10.2-3.7 15.2-1.6zM160 256a96 96 0 1 1 192 0 96 96 0 1 1 -192 0zm224 0a128 128 0 1 0 -256 0 128 128 0 1 0 256 0z"></path>
        </svg>
    `;
    const moonSVG = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">
            <path d="M223.5 32C100 32 0 132.3 0 256S100 480 223.5 480c60.6 0 115.5-24.2 155.8-63.4c5-4.9 6.3-12.5 3.1-18.7s-10.1-9.7-17-8.5c-9.8 1.7-19.8 2.6-30.1 2.6c-96.9 0-175.5-78.8-175.5-176c0-65.8 36-123.1 89.3-153.3c6.1-3.5 9.2-10.5 7.7-17.3s-7.3-11.9-14.3-12.5c-6.3-.5-12.6-.8-19-.8z"></path>
        </svg>
    `;

    // Check the saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.toggle('dark-mode', savedTheme === 'dark');
        themeToggle.innerHTML = savedTheme === 'dark' ? moonSVG : sunSVG;
        sidebar.classList.toggle('dark-mode', savedTheme === 'dark');
    } else {
        // Default to light theme if no saved preference
        themeToggle.innerHTML = sunSVG;
    }

    // Add click event to toggle theme
    themeToggle.addEventListener('click', () => {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        themeToggle.innerHTML = isDarkMode ? moonSVG : sunSVG;
        sidebar.classList.toggle('dark-mode', isDarkMode);
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    });
});

// ----------------------------------------
// Add a clickable '#' for each heading 
// that directs to that heading
// ----------------------------------------
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach(header => {
        if (!header.id) {
            let text = header.textContent.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^\w\-]/g, '');
            header.id = text;
        }

        // Avoid adding duplicate links if the script runs multiple times
        if (!header.querySelector(".headerlink")) {
            let link = document.createElement("a");
            link.className = "headerlink";
            link.href = `#${header.id}`;
            link.title = "Link to this heading";
            link.textContent = " #"; // Space before # for spacing

            header.appendChild(link);
        }
    });
});

// ----------------------------------------
// Code syntax highlighting
// ----------------------------------------

// Remove the leading whitespace/newlines around code blocks 
// caused by the html structure used for readability
document.addEventListener("DOMContentLoaded", function() {
    // Select all code blocks
    const codeBlocks = document.querySelectorAll('.code-cell code.language-python');

    codeBlocks.forEach(function(block) {
        // Apply syntax highlighting to the code block
        // Note: The below line is not needed with this setup
        //  but may be useful in the case that the method
        //  is later changed
        // Prism.highlightElement(block);

        // Get the code with highlighted classes
        const highlightedHTML = block.innerHTML;

        // Remove leading/trailing whitespace/newlines
        block.innerHTML = highlightedHTML.trim();
    });

    // Select all output-code blocks
    const outputBlocks = document.querySelectorAll('.output-cell .output-code');

    outputBlocks.forEach(function(block) {
        // Remove unwanted leading/trailing whitespace or newlines
        block.textContent = block.textContent.trim();
    });
});

// ----------------------------------------
// Copy button on code cells
// ----------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.code-cell').forEach(cell => {
        // Avoid inserting the button multiple times
        if (cell.querySelector('.copy-button')) return;

        const button = document.createElement('button');
        button.className = 'copy-button';

        // Define copy icon and text
        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 0.25em;">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>Copy</span>
        `;

        // copy text and add click effects
        button.addEventListener('click', () => {
            // const code = cell.innerText;
            const code = cell.querySelector('code').innerText;
            navigator.clipboard.writeText(code).then(() => {
                button.querySelector('span').textContent = 'Copied!';
                setTimeout(() => {
                    button.querySelector('span').textContent = 'Copy';
                }, 1000);
            });
        });

        cell.appendChild(button);
    });
});

document.querySelectorAll(".collapsible-header").forEach(header => {
    header.addEventListener("click", function () {
        const section = this.closest(".collapsible-section"); // Get parent section
        section.classList.toggle("active");
        this.classList.toggle("active"); // Keep this for toggling the plus/minus sign

        const content = section.querySelector(".collapsible-content");
        content.style.display = content.style.display === "block" ? "none" : "block";
    });
});

// ----------------------------------------
// Style standard markdown table
// ----------------------------------------
//     Notes:
//     To apply the standard markdown table formatting, insert the 
//     following code (including the new line) before your table in 
//     your markdown file.
//         ```
//         <div class="md_table md_table--equal-cols">

//         ```
//     Additionally, you must close the div element as follows, 
//     again including the new line.
//         ```

//         </div>
//         ```
//     Note that the "md_table--equal-cols" class is an optional
//     addition that ensures the columns widths are equal. 

// set equal column widths when the --equal-cols class is added 
// to the div

document.querySelectorAll('.md_table.md-equal-cols').forEach(container => {
    const table = container.querySelector('table');
    if (!table) return;

    // Get number of columns from first row's cells
    const firstRow = table.querySelector('tr');
    if (!firstRow) return;

    const colCount = firstRow.children.length;
    container.style.setProperty('--col-count', colCount);
});

// blur the table edges when scroll is present
document.querySelectorAll('.md_table').forEach(container => {
    // Create wrapper div with relative position
    const wrapper = document.createElement('div');
    wrapper.className = 'md_table-wrapper';
    wrapper.style.position = 'relative';

    // Move container into wrapper
    container.parentNode.insertBefore(wrapper, container);
    wrapper.appendChild(container);

    // Create blur overlays
    const leftBlur = document.createElement('div');
    const rightBlur = document.createElement('div');
    leftBlur.className = 'md-table-blur left';
    rightBlur.className = 'md-table-blur right';

    wrapper.appendChild(leftBlur);
    wrapper.appendChild(rightBlur);

    // Position blur overlays inside wrapper
    const positionBlur = () => {
        leftBlur.style.top = '0';
        leftBlur.style.left = '0';
        leftBlur.style.height = '100%';

        rightBlur.style.top = '0';
        rightBlur.style.right = '0';
        rightBlur.style.height = '100%';
    };

  // Update blur opacity based on scroll position
    const updateBlur = () => {
        const scrollLeft = container.scrollLeft;
        const maxScrollLeft = container.scrollWidth - container.clientWidth;

        leftBlur.style.opacity = scrollLeft > 0 ? 1 : 0;
        rightBlur.style.opacity = scrollLeft < maxScrollLeft ? 1 : 0;
        positionBlur();
    };

    container.addEventListener('scroll', updateBlur);
    window.addEventListener('resize', updateBlur);
    updateBlur();
});

// ----------------------------------------
// Check for mobile devices
// ----------------------------------------
function isMobileDevice() {
    return /Mobi|Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

if (isMobileDevice()) {
    document.body.classList.add("is-mobile");
}