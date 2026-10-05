function initSettings() {

    // =========================================
    // THEME
    // =========================================

    updateThemeSelection(
        document.documentElement.dataset.theme
    );


    // =========================================
    // ANIMATIONS
    // =========================================

    const toggle =
        document.getElementById("animations-toggle");

    if (!toggle) {
        return;
    }

    const savedAnimations =
        localStorage.getItem("animations");

    // Animations are enabled by default.
    const animationsEnabled =
        savedAnimations !== "false";

    applyAnimationsSetting(animationsEnabled);


    toggle.addEventListener("click", () => {

        const currentlyEnabled =
            document.documentElement.dataset.animations !== "off";

        applyAnimationsSetting(!currentlyEnabled);

    });
}


/* =========================================================
   ANIMATIONS SETTING
   ========================================================= */

function applyAnimationsSetting(enabled) {

    const toggle =
        document.getElementById("animations-toggle");

    if (enabled) {

        document.documentElement.dataset.animations = "on";

        localStorage.setItem(
            "animations",
            "true"
        );

        if (toggle) {
            toggle.classList.add("active");
            toggle.setAttribute(
                "aria-pressed",
                "true"
            );
        }

    } else {

        document.documentElement.dataset.animations = "off";

        localStorage.setItem(
            "animations",
            "false"
        );

        if (toggle) {
            toggle.classList.remove("active");
            toggle.setAttribute(
                "aria-pressed",
                "false"
            );
        }
    }
}