(() => {
    const result = document.getElementById("result");
    if (result) {
        result.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
    }

    const form = document.getElementById("car-evaluation-form");
    if (form) {
        form.addEventListener("submit", event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                form.reportValidity();
            }
        });
    }
})();
