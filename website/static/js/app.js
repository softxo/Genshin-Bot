document.addEventListener("DOMContentLoaded", () => {

    const mainContent = document.querySelector(".main-content");

    if (!mainContent) {
        return;
    }

    async function navigate(url, addToHistory = true) {

        try {

            const response = await fetch(url);

            if (
                response.redirected &&
                new URL(response.url).pathname === "/verify"
            ) {
                history.pushState(
                    {},
                    "",
                    "/verify"
                );

                window.location.href = "/verify";

                return;
            }

            if (!response.ok) {
                throw new Error(
                    `Navigation failed: ${response.status}`
                );
            }

            const html = await response.text();

            const parser = new DOMParser();

            const newDocument =
                parser.parseFromString(
                    html,
                    "text/html"
                );

            const requestedPath =
                new URL(
                    url,
                    window.location.origin
                ).pathname;

            const returnedTitle =
                newDocument.title;

            const newMain =
                newDocument.querySelector(
                    ".main-content"
                );

            if (!newMain) {
                throw new Error(
                    "New page does not contain .main-content"
                );
            }

            const isVerificationPage =
                newDocument.querySelector(
                    ".verification-page"
                );

            if (
                isVerificationPage &&
                requestedPath !== "/verify"
            ) {

                history.pushState(
                    {},
                    "",
                    "/verify"
                );

            }


            /*
             * Replace the page content.
             */

            mainContent.innerHTML =
                newMain.innerHTML;


            /*
             * Execute scripts from the new page.
             */

            mainContent
                .querySelectorAll("script")
                .forEach(oldScript => {

                    const newScript =
                        window.document.createElement("script");

                    /*
                     * Copy attributes.
                     */

                    for (
                        const attribute
                        of oldScript.attributes
                    ) {

                        newScript.setAttribute(
                            attribute.name,
                            attribute.value
                        );

                    }

                    /*
                     * Copy inline JavaScript.
                     */

                    newScript.textContent =
                        oldScript.textContent;

                    /*
                     * Replace the inert script with
                     * an executable one.
                     */

                    oldScript.replaceWith(
                        newScript
                    );

                });


            /*
             * Update browser history.
             */

            if (addToHistory) {

                history.pushState(
                    {},
                    "",
                    url
                );

            }


            /*
             * Update active sidebar item.
             */

            updateActiveNavigation(url);


            /*
             * Scroll to the top.
             */

            window.scrollTo({
                top: 0,
                behavior: "instant"
            });


        } catch (error) {

            console.error(
                "Navigation error:",
                error
            );

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

const mobileMenuButton = document.getElementById("mobile-menu-button");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebar-overlay");


function openSidebar() {

    sidebar?.classList.add("open");

    sidebarOverlay?.classList.add("visible");

    mobileMenuButton?.classList.add("open");

    mobileMenuButton?.setAttribute(
        "aria-expanded",
        "true"
    );
}


function closeSidebar() {

    sidebar?.classList.remove("open");

    sidebarOverlay?.classList.remove("visible");

    mobileMenuButton?.classList.remove("open");

    mobileMenuButton?.setAttribute(
        "aria-expanded",
        "false"
    );
}


mobileMenuButton?.addEventListener("click", () => {

    if (sidebar?.classList.contains("open")) {
        closeSidebar();
    } else {
        openSidebar();
    }

});


sidebarOverlay?.addEventListener(
    "click",
    closeSidebar
);


sidebar?.querySelectorAll("a").forEach(link => {

    link.addEventListener(
        "click",
        closeSidebar
    );

});