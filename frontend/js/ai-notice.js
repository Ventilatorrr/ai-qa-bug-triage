// One browser preference for New/Edit. Dismissal is informational, not consent.
(() => {
    const preferenceKey = "ai-data-sharing-notice-dismissed";
    let dismissed = false;
    const notices = Array.from(document.querySelectorAll(".ai-assist-disclosure")).map(notice => ({
        notice,
        text: notice.querySelector("p"),
        button: document.getElementById(notice.dataset.aiButton),
        dismiss: notice.querySelector(".ai-notice-dismiss")
    }));

    function update() {
        for (const {notice, text, button} of notices) {
            const visible = !dismissed && !button.hidden;
            notice.hidden = !visible;
            const descriptions = (button.getAttribute("aria-describedby") || "")
                .split(/\s+/).filter(id => id && id !== text.id);
            if (visible) descriptions.push(text.id);
            if (descriptions.length) button.setAttribute("aria-describedby", descriptions.join(" "));
            else button.removeAttribute("aria-describedby");
        }
    }

    function restore() {
        try { dismissed = localStorage.getItem(preferenceKey) === "1"; }
        catch (error) { /* Keep the in-page dismissal if storage is unavailable. */ }
        update();
    }

    for (const {button, dismiss} of notices) {
        dismiss.addEventListener("click", () => {
            dismissed = true;
            try { localStorage.setItem(preferenceKey, "1"); }
            catch (error) { /* Dismissal still works for this page. */ }
            update();
            if (!button.hidden) {
                const next = button.disabled
                    ? button.form.querySelector(".ai-suggestions-footer:not([hidden]) button") ||
                      button.form.querySelector(".creation-form-actions button:not([disabled]):not([hidden])")
                    : button;
                next?.focus({preventScroll: true});
            }
        });
        new MutationObserver(update).observe(button, {attributes: true, attributeFilter: ["hidden"]});
    }
    window.addEventListener("pageshow", restore);
    window.addEventListener("storage", event => {
        if (event.key === preferenceKey || event.key === null) restore();
    });
    restore();
})();
