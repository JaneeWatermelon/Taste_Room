function adjustInputWidth(inputElement) {
    const tempSpan = document.createElement('span');
    tempSpan.style.visibility = 'hidden';
    tempSpan.style.whiteSpace = 'pre';
    tempSpan.style.fontSize = window.getComputedStyle(inputElement).fontSize;
    tempSpan.style.fontFamily = window.getComputedStyle(inputElement).fontFamily;
    tempSpan.style.padding = window.getComputedStyle(inputElement).padding;
    tempSpan.textContent = inputElement.value || inputElement.placeholder;
    $(tempSpan).css('width', 'fit-content');
    document.body.appendChild(tempSpan);
    inputElement.style.width = `${tempSpan.offsetWidth}px`;
    document.body.removeChild(tempSpan);
}

document.querySelectorAll('.input_wrapper.fit > input').forEach(input => {
    input.addEventListener('input', () => adjustInputWidth(input));
    window.addEventListener('load', () => adjustInputWidth(input));
    window.addEventListener('resize', () => adjustInputWidth(input));
});
