
// ----------------------------------------
// Style expandable markdown table
// ----------------------------------------
// Caution:
// This code likely needs to be refactored to more closely
// match the "Style standard markdown table" section
//
// Notes:
// To apply the expanded markdown table formatting, insert the 
// following code (including the new line) before your table in 
// your markdown file.
//     ```
//     <div class="expandable-table">

//     ```
// Additionally, you must close the div element as follows, 
// again including the new line.
//     ```

//     </div>
//     ```

document.querySelectorAll('.expandable-table').forEach(container => {
    // create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'expandable-table-wrapper';
    wrapper.style.position = 'relative';

    // move container into wrapper
    container.parentNode.insertBefore(wrapper, container);
    wrapper.appendChild(container);

    // create expand button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'expand-toggle';
    toggleBtn.innerHTML = '⤢';
    wrapper.appendChild(toggleBtn);

    // create blur overlays
    const leftBlur = document.createElement('div');
    const rightBlur = document.createElement('div');
    leftBlur.className = 'expandable-table-blur left';
    rightBlur.className = 'expandable-table-blur right';
    wrapper.appendChild(leftBlur);
    wrapper.appendChild(rightBlur);

    // set blur position
    const positionBlur = () => {
        leftBlur.style.top = '0';
        leftBlur.style.left = '0';
        leftBlur.style.height = '100%';

        rightBlur.style.top = '0';
        rightBlur.style.right = '0';
        rightBlur.style.height = '100%';
    };

    // update blur opacity based on state (expanded vs. collapsed)
    const updateBlur = () => {
        const isExpanded = container.classList.contains('expand');
        if (!isExpanded) {
            leftBlur.style.opacity = 0;
            rightBlur.style.opacity = 0;
            return;
        }

        const scrollLeft = container.scrollLeft;
        const maxScrollLeft = container.scrollWidth - container.clientWidth;

        leftBlur.style.opacity = scrollLeft > 0 ? 1 : 0;
        rightBlur.style.opacity = scrollLeft < maxScrollLeft ? 1 : 0;
        positionBlur();
    };

    // toggle the state (expanded vs. collapsed)
    toggleBtn.addEventListener('click', () => {
        container.classList.toggle('expand');
        // toggleBtn.innerHTML = container.classList.contains('expand') ? '⤡' : '⤢';
        updateBlur(); // Resync blur
    });

    // conditionally update blur
    container.addEventListener('scroll', updateBlur);
    window.addEventListener('resize', updateBlur);
    updateBlur();
});
