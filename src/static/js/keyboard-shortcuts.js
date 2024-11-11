class KeyboardShortcuts {
    constructor() {
        this.shortcuts = {
            edit: {
                key: 'e',
                modifier: 'Alt',
                selector: 'a[data-edit-link]'
            },
            create: {
                key: 'c',
                modifier: 'Alt',
                selector: 'a[data-create-link]'
            },
            lambda: {
                key: 'Backquote',
                modifier: 'Alt',
                action: () => this.insertTextAtCaret('λ#()#')
            }
        };
        
        this.init();
    }

    init() {
        document.addEventListener('keydown', (event) => this.handleKeydown(event));
    }

    handleKeydown(event) {
        if (!event.altKey) return;

        for (const [name, shortcut] of Object.entries(this.shortcuts)) {
            if (event.key.toLowerCase() === shortcut.key.toLowerCase() || 
                event.code === shortcut.key) {
                event.preventDefault();
                
                if (shortcut.action) {
                    shortcut.action();
                } else {
                    this.navigateToLink(shortcut.selector);
                }
            }
        }
    }

    navigateToLink(selector) {
        const link = document.querySelector(selector);
        if (link) {
            window.location.href = link.href;
        }
    }

    insertTextAtCaret(text) {
        const activeElement = document.activeElement;
        if (!activeElement || !['INPUT', 'TEXTAREA'].includes(activeElement.tagName)) {
            console.warn('No input field or textarea is active.');
            return;
        }

        const startPos = activeElement.selectionStart;
        const endPos = activeElement.selectionEnd;
        const originalText = activeElement.value;
        
        activeElement.value = originalText.slice(0, startPos) + 
                            text + 
                            originalText.slice(endPos);

        // Move the caret just after the '(' in the inserted text
        const newCaretPosition = startPos + text.indexOf('(') + 1;
        activeElement.setSelectionRange(newCaretPosition, newCaretPosition);
        activeElement.focus();
    }
}

// Initialize keyboard shortcuts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new KeyboardShortcuts();
});
