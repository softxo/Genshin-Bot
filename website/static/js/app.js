document.addEventListener("DOMContentLoaded", () => {

    const mainContent = document.querySelector(".main-content");

    if (!mainContent) {
        return;
    }

    async function navigate(url, addToHistory = true) {

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Navigation failed: ${response.status}`);
            }

            const html = await response.text();

            const parser = new DOMParser();
            const document = parser.parseFromString(html, "text/html");

            const newMain = document.querySelector(".main-content");

            if (!newMain) {
                throw new Error("New page does not contain .main-content");
            }

            mainContent.innerHTML = newMain.innerHTML;

            if (addToHistory) {
                history.pushState({}, "", url);
            }

            updateActiveNavigation(url);

            window.scrollTo({
                top: 0,
                behavior: "instant"
            });

        } catch (error) {
            console.error("Navigation error:", error);

            window.location.href = url;
        }
    }


    function updateActiveNavigation(url) {

        const currentPath = new URL(url, window.location.origin).pathname;

        document.querySelectorAll(".nav-item").forEach(item => {

            const itemPath = new URL(
                item.href,
                window.location.origin
            ).pathname;

            item.classList.toggle(
                "active",
                itemPath === currentPath
            );

        });
    }


    document.addEventListener("click", event => {

        const link = event.target.closest("a");

        if (!link) {
            return;
        }

        if (link.origin !== window.location.origin) {
            return;
        }

        if (
            event.ctrlKey ||
            event.shiftKey ||
            event.altKey ||
            event.metaKey ||
            link.target === "_blank"
        ) {
            return;
        }

        if (link.pathname === window.location.pathname &&
            link.hash) {
            return;
        }

        event.preventDefault();

        navigate(link.href);
    });


    window.addEventListener("popstate", () => {
        navigate(window.location.href, false);
    });

});