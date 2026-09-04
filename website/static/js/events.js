function initEvents() {

    let expirationRefreshTime = null;

    function initialiseEventsDropdown() {

        const select =
            document.getElementById("events-account");

        if (!select) {
            return;
        }

        const button =
            select.querySelector(
                ".custom-select-button"
            );

        if (!button) {
            return;
        }

        button.addEventListener(
            "click",
            event => {

                event.stopPropagation();

                select.classList.toggle("open");

            }
        );

        document.addEventListener(
            "click",
            () => {

                select.classList.remove("open");

            }
        );
    }


    function initialiseEventFeatureToggles() {

        const cards =
            document.querySelectorAll(
                ".event-featured-card"
            );

        cards.forEach(card => {

            const button =
                card.querySelector(
                    ".event-featured-toggle"
                );

            if (!button) {
                return;
            }

            button.addEventListener(
                "click",
                event => {

                    event.stopPropagation();

                    const collapsed =
                        card.classList.toggle(
                            "collapsed"
                        );

                    button.setAttribute(
                        "aria-expanded",
                        String(!collapsed)
                    );

                    button.setAttribute(
                        "aria-label",
                        collapsed
                            ? "Expand event"
                            : "Collapse event"
                    );

                }
            );

        });

    }


    function updateEventTimeLeft() {

        const timers =
            document.querySelectorAll(
                ".event-time-left[data-end-time]"
            );

        const now =
            Math.floor(
                Date.now() / 1000
            );


        timers.forEach(timer => {

            const endTime =
                Number(
                    timer.dataset.endTime
                );

            const remaining =
                endTime - now;


            if (remaining <= 0) {

                timer.textContent =
                    "Updating...";

                timer.classList.remove(
                    "warning"
                );

                timer.classList.add(
                    "danger"
                );


                if (
                    expirationRefreshTime !== endTime &&
                    typeof window.refreshEvents ===
                        "function"
                ) {

                    expirationRefreshTime =
                        endTime;

                    window.refreshEvents();

                }

                return;
            }


            const days =
                Math.floor(
                    remaining / 86400
                );

            const hours =
                Math.floor(
                    (remaining % 86400) / 3600
                );

            const minutes =
                Math.floor(
                    (remaining % 3600) / 60
                );


            if (days > 0) {

                timer.textContent =
                    `${days}d ${hours}h left`;

            } else if (hours > 0) {

                timer.textContent =
                    `${hours}h ${minutes}m left`;

            } else {

                timer.textContent =
                    `${minutes}m left`;

            }


            timer.classList.remove(
                "warning",
                "danger"
            );


            if (
                timer.classList.contains(
                    "event-daily-reset"
                )
            ) {

                if (remaining < 14400) {

                    timer.classList.add(
                        "danger"
                    );

                } else if (remaining < 54000) {

                    timer.classList.add(
                        "warning"
                    );

                }

            } else {

                if (remaining < 86400) {

                    timer.classList.add(
                        "danger"
                    );

                } else if (remaining < 259200) {

                    timer.classList.add(
                        "warning"
                    );

                }

            }

        });

    }


    async function refreshEvents() {

        if (window.eventsRefreshing) {
            return;
        }

        window.eventsRefreshing = true;


        try {

            const container =
                document.querySelector(
                    ".events-page"
                );

            if (!container) {
                return;
            }


            /*
             * Remember which featured cards are currently expanded.
             */

            const expandedCards = [];

            document
                .querySelectorAll(
                    ".event-featured-card"
                )
                .forEach((card, index) => {

                    expandedCards[index] =
                        !card.classList.contains(
                            "collapsed"
                        );

                });


            /*
             * Remember the current scroll position.
             */

            const scrollPosition =
                window.scrollY;


            /*
             * Request fresh Events HTML.
             */

            const response =
                await fetch(
                    `/events/refresh?account_id=${
                        document
                            .getElementById(
                                "daily-commissions"
                            )
                            ?.dataset.accountId || ""
                    }`,
                    {
                        credentials: "same-origin",
                        cache: "no-store",
                    }
                );


            if (!response.ok) {
                return;
            }


            const html =
                await response.text();


            /*
             * Parse the returned page without replacing the actual document.
             */

            const parser =
                new DOMParser();

            const documentFromServer =
                parser.parseFromString(
                    html,
                    "text/html"
                );


            const newFeatured =
                documentFromServer.querySelector(
                    ".events-featured"
                );

            const newEventsList =
                documentFromServer.querySelector(
                    ".events-list"
                );


            const currentFeatured =
                container.querySelector(
                    ".events-featured"
                );

            const currentEventsList =
                container.querySelector(
                    ".events-list"
                );


            if (
                !newFeatured ||
                !newEventsList ||
                !currentFeatured ||
                !currentEventsList
            ) {

                return;

            }


            /*
             * Replace only the dynamic Events content.
             */

            currentFeatured.replaceWith(
                newFeatured
            );

            currentEventsList.replaceWith(
                newEventsList
            );


            /*
             * Restore expanded/collapsed state.
             */

            document
                .querySelectorAll(
                    ".event-featured-card"
                )
                .forEach((card, index) => {

                    if (
                        expandedCards[index]
                    ) {

                        card.classList.remove(
                            "collapsed"
                        );

                        const button =
                            card.querySelector(
                                ".event-featured-toggle"
                            );

                        if (button) {

                            button.setAttribute(
                                "aria-expanded",
                                "true"
                            );

                            button.setAttribute(
                                "aria-label",
                                "Collapse event"
                            );

                        }

                    }

                });


            /*
             * Re-bind the feature toggles after replacing the cards.
             */

            initialiseEventFeatureToggles();


            /*
             * Recalculate timers immediately.
             */

            updateEventTimeLeft();


            /*
             * Restore scroll position.
             */

            window.scrollTo(
                0,
                scrollPosition
            );

        } catch (error) {

            console.error(
                "Failed to refresh Events:",
                error
            );

        } finally {

            window.eventsRefreshing =
                false;

            scheduleEventsRefresh();

        }

    }


    /*
     * Expose the refresh function before
     * any timers can call it.
     */

    window.refreshEvents =
        refreshEvents;


    initialiseEventsDropdown();

    initialiseEventFeatureToggles();

    updateEventTimeLeft();


    /*
     * Countdown updates every second.
     */

    if (window.eventsTimer) {

        clearInterval(
            window.eventsTimer
        );

    }

    window.eventsTimer =
        setInterval(
            updateEventTimeLeft,
            1000
        );


        /*
        * Adaptive event-data refreshing.
        */

    function scheduleEventsRefresh() {

        if (window.eventsRefreshTimer) {

            clearTimeout(
                window.eventsRefreshTimer
            );

        }


        const timers =
            document.querySelectorAll(
                ".event-time-left[data-end-time]"
            );


        const now =
            Math.floor(
                Date.now() / 1000
            );


        let nearExpiry = false;


        timers.forEach(timer => {

            const endTime =
                Number(
                    timer.dataset.endTime
                );

            const remaining =
                endTime - now;


            if (
                remaining > 0 &&
                remaining <= 300
            ) {

                nearExpiry = true;

            }

        });


        /*
        * Normal:
        *     refresh every 60 seconds
        *
        * Near an event/reset:
        *     refresh every 10 seconds
        */

        const delay =
            nearExpiry
                ? 10000
                : 10000;


        window.eventsRefreshTimer =
            setTimeout(
                refreshEvents,
                delay
            );

    }


    /*
    * Start adaptive refreshing.
    */

    scheduleEventsRefresh();


        document.addEventListener(
            "visibilitychange",
            () => {
    
                if (
                    document.visibilityState ===
                    "visible"
                ) {
    
                    if (
                        typeof window.refreshEvents ===
                        "function"
                    ) {
    
                        window.refreshEvents();
    
                    }
    
                }
    
            }
        );

}


window.initEvents =
    initEvents;