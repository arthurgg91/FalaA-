document.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const buttons = document.querySelectorAll('[data-font]');

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const currentSize = parseFloat(getComputedStyle(root).fontSize);
      const direction = button.dataset.font;
      const nextSize = direction === 'increase' ? currentSize + 1 : currentSize - 1;

      if (nextSize >= 14 && nextSize <= 22) {
        root.style.fontSize = `${nextSize}px`;
      }
    });
  });
});
