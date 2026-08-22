document.addEventListener("DOMContentLoaded", () => {

    const mainContent = document.querySelector(".main-content");

    if (!mainContent) {
        return;
    }

    async function navigate(url, addToHistory = true) {

        try {

            const response = await fetch(
                url,
                {
                    redirect: "manual"
                }
            );


            /*
             * Handle server-side redirects.
             */

            if (
                response.status === 301 ||
                response.status === 302 ||
                response.status === 303 ||
                response.status === 307 ||
                response.status === 308
            ) {

                const redirectUrl =
                    response.headers.get("Location");

                if (redirectUrl) {

                    window.location.href =
                        new URL(
                            redirectUrl,
                            window.location.origin
                        ).href;

                    return;
                }
            }


            if (!response.ok) {

                throw new Error(
                    `Navigation failed: ${response.status}`
                );

            }


            const html =
                await response.text();


            const parser =
                new DOMParser();


            const newDocument =
                parser.parseFromString(
                    html,
                    "text/html"
                );


            const newMain =
                newDocument.querySelector(
                    ".main-content"
                );


            if (!newMain) {

                throw new Error(
                    "New page does not contain .main-content"
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
                        window.document.createElement(
                            "script"
                        );


                    for (
                        const attribute
                        of oldScript.attributes
                    ) {

                        newScript.setAttribute(
                            attribute.name,
                            attribute.value
                        );

                    }


                    newScript.textContent =
                        oldScript.textContent;


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
             * Initialize page-specific functionality.
             */

            const finalPath =
                new URL(
                    url,
                    window.location.origin
                ).pathname;


            if (
                finalPath === "/planner" &&
                typeof window.initPlanner === "function"
            ) {

                window.initPlanner();

            }


            if (
                finalPath === "/achievements" &&
                typeof window.initAchievements === "function"
            ) {

                window.initAchievements();

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


            window.location.href =
                url;

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