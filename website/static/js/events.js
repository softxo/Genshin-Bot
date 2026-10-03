function initEvents() {

    // =========================================
    // PAGE
    // =========================================

    const eventsPage =
        document.querySelector(".events-page");

    if (!eventsPage) {
        return;
    }


    // =========================================
    // ACCOUNT DROPDOWN
    // =========================================

    function initialiseEventsDropdown() {

        const dropdown =
            document.getElementById("events-account");

        if (!dropdown) {
            return;
        }

        const button =
            dropdown.querySelector(
                ".custom-select-button"
            );

        if (!button) {
            return;
        }


        // Prevent duplicate listeners.
        if (button.dataset.initialised === "true") {
            return;
        }

        button.dataset.initialised = "true";


        button.addEventListener(
            "click",
            (event) => {

                event.preventDefault();
                event.stopPropagation();

                dropdown.classList.toggle("open");

            }
        );


        // Close after selecting an account.
        const options =
            dropdown.querySelectorAll(
                ".custom-select-option"
            );


        options.forEach(option => {

            option.addEventListener(
                "click",
                event => {

                    event.preventDefault();
                    event.stopPropagation();


                    const accountId =
                        option.dataset.accountId;

                    if (!accountId) {
                        return;
                    }


                    dropdown.classList.remove(
                        "open"
                    );


                    window.location.href =
                        `/events?account_id=${accountId}`;

                }
            );

        });

    }


    // =========================================
    // CLOSE ACCOUNT DROPDOWN
    // =========================================

    function initialiseDropdownClose() {

        if (window.eventsDropdownCloseInitialised) {
            return;
        }

        window.eventsDropdownCloseInitialised = true;


        document.addEventListener(
            "click",
            (event) => {

                const dropdown =
                    document.getElementById(
                        "events-account"
                    );

                if (!dropdown) {
                    return;
                }

                if (!dropdown.contains(event.target)) {

                    dropdown.classList.remove(
                        "open"
                    );

                }

            }
        );

    }


    // =========================================
    // FEATURED EVENT CARDS
    // =========================================

    function initialiseEventFeatureToggles() {

        document
            .querySelectorAll(
                ".event-featured-toggle"
            )
            .forEach(toggle => {

                if (
                    toggle.dataset.initialised ===
                    "true"
                ) {
                    return;
                }

                toggle.dataset.initialised =
                    "true";


                toggle.addEventListener(
                    "click",
                    (event) => {

                        event.preventDefault();
                        event.stopPropagation();


                        const card =
                            toggle.closest(
                                ".event-featured-card"
                            );

                        if (!card) {
                            return;
                        }


                        const collapsed =
                            card.classList.toggle(
                                "collapsed"
                            );


                        toggle.setAttribute(
                            "aria-expanded",
                            collapsed
                                ? "false"
                                : "true"
                        );

                    }
                );

            });

    }


    // =========================================
    // OVERVIEW TABS
    // =========================================

    function initialiseOverviewTabs() {

        document
            .querySelectorAll(
                ".events-overview-tab"
            )
            .forEach(tab => {

                if (
                    tab.dataset.initialised ===
                    "true"
                ) {
                    return;
                }

                tab.dataset.initialised =
                    "true";


                tab.addEventListener(
                    "click",
                    () => {

                        const target =
                            tab.dataset.overviewTab;

                        if (!target) {
                            return;
                        }


                        document
                            .querySelectorAll(
                                ".events-overview-tab"
                            )
                            .forEach(otherTab => {

                                otherTab.classList.toggle(
                                    "active",
                                    otherTab === tab
                                );

                            });


                        document
                            .querySelectorAll(
                                ".events-overview-panel"
                            )
                            .forEach(panel => {

                                panel.classList.toggle(
                                    "active",
                                    panel.dataset.overviewPanel === target
                                );

                            });

                    }
                );

            });

    }


    // =========================================
    // EVENT COUNTDOWN TIMERS
    // =========================================

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

            if (!endTime) {
                return;
            }


            const originalRemaining =
                endTime - now;


            // -----------------------------------------
            // EXPIRED
            // -----------------------------------------

            if (originalRemaining <= 0) {

                timer.textContent =
                    timer.classList.contains(
                        "stygian-reset-timer"
                    )
                        ? "Resetting..."
                        : "Updating...";


                timer.classList.add(
                    "expired"
                );


                timer.classList.remove(
                    "warning",
                    "danger"
                );


                return;
            }


            // -----------------------------------------
            // ACTIVE
            // -----------------------------------------

            timer.classList.remove(
                "expired"
            );


            const days =
                Math.floor(
                    originalRemaining / 86400
                );

            const hours =
                Math.floor(
                    (originalRemaining % 86400) /
                    3600
                );

            const minutes =
                Math.floor(
                    (originalRemaining % 3600) /
                    60
                );


            if (days > 0) {

                timer.textContent =
                    `${days}d ${hours}h ${minutes}m`;

            } else if (hours > 0) {

                timer.textContent =
                    `${hours}h ${minutes}m`;

            } else {

                timer.textContent =
                    `${minutes}m`;

            }


            // =========================================
            // TIME STATUS
            // =========================================

            timer.classList.remove(
                "warning",
                "danger"
            );


            // Less than 1 day remaining.
            if (originalRemaining < 86400) {

                timer.classList.add(
                    "danger"
                );


            // Less than 3 days remaining.
            } else if (originalRemaining < 259200) {

                timer.classList.add(
                    "warning"
                );

            }

        });


        // =========================================
        // OVERVIEW RESIN COUNTDOWNS
        // =========================================

        document
            .querySelectorAll(
                ".overview-resin-timer[data-resin-timestamp]"
            )
            .forEach(timer => {

                const timestamp = Number(
                    timer.dataset.resinTimestamp
                );

                if (!timestamp) {
                    timer.textContent = "Full";
                    return;
                }

                const remaining = Math.max(
                    0,
                    timestamp - Math.floor(
                        Date.now() / 1000
                    )
                );

                if (remaining === 0) {
                    timer.textContent = "Now";
                    return;
                }

                const hours = Math.floor(
                    remaining / 3600
                );

                const minutes = Math.floor(
                    (remaining % 3600) / 60
                );

                const seconds = remaining % 60;

                if (hours > 0) {

                    timer.textContent =
                        `${hours}h ${minutes}m`;

                } else {

                    timer.textContent =
                        `${minutes}m ${seconds}s`;

                }

            });

    }



    // =========================================
    // REFRESH EVENTS
    // =========================================

    async function refreshEvents() {

        if (window.eventsRefreshing) {
            return;
        }

        window.eventsRefreshing = true;


        try {

            const currentPage =
                document.querySelector(
                    ".events-page"
                );

            if (!currentPage) {
                return;
            }


            // -----------------------------------------
            // Current page state
            // -----------------------------------------

            const isOverview =
                currentPage.dataset.overview ===
                "true";


            const accountId =
                currentPage.dataset.accountId ||
                "";


            // -----------------------------------------
            // Preserve UI state
            // -----------------------------------------

            const expandedCards =
                Array.from(
                    currentPage.querySelectorAll(
                        ".event-featured-card:not(.collapsed)"
                    )
                ).map(card =>
                    card.dataset.eventType
                );


            const activeOverviewTab =
                currentPage
                    .querySelector(
                        ".events-overview-tab.active"
                    )
                    ?.dataset.overviewTab ||
                "daily";


            const scrollPosition =
                window.scrollY;


            // -----------------------------------------
            // Build request
            // -----------------------------------------

            const params =
                new URLSearchParams();


            if (isOverview) {

                params.set(
                    "overview",
                    "true"
                );

            }


            if (accountId) {

                params.set(
                    "account_id",
                    accountId
                );

            }


            const response =
                await fetch(
                    `/events/refresh?${params.toString()}`
                );


            if (!response.ok) {
                return;
            }


            const html =
                await response.text();


            const parser =
                new DOMParser();


            const documentHTML =
                parser.parseFromString(
                    html,
                    "text/html"
                );


            const newPage =
                documentHTML.querySelector(
                    ".events-page"
                );


            if (!newPage) {
                return;
            }


            // -----------------------------------------
            // Replace page
            // -----------------------------------------

            currentPage.replaceWith(
                newPage
            );


            // -----------------------------------------
            // Restore expanded cards
            // -----------------------------------------

            expandedCards.forEach(
                eventType => {

                    const card =
                        document.querySelector(
                            `.event-featured-card[data-event-type="${eventType}"]`
                        );

                    if (!card) {
                        return;
                    }


                    card.classList.remove(
                        "collapsed"
                    );


                    const toggle =
                        card.querySelector(
                            ".event-featured-toggle"
                        );


                    if (toggle) {

                        toggle.setAttribute(
                            "aria-expanded",
                            "true"
                        );

                    }

                }
            );


            // -----------------------------------------
            // Reinitialise controls
            // -----------------------------------------

            initialiseEventsDropdown();

            initialiseEventFeatureToggles();

            initialiseOverviewTabs();

            updateEventTimeLeft();


            // -----------------------------------------
            // Restore overview tab
            // -----------------------------------------

            if (isOverview) {

                const activeTab =
                    document.querySelector(
                        `.events-overview-tab[data-overview-tab="${activeOverviewTab}"]`
                    );


                if (activeTab) {

                    activeTab.click();

                }

            }


            // -----------------------------------------
            // Restore scroll position
            // -----------------------------------------

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

        }

    }


    // =========================================
    // GLOBAL REFRESH
    // =========================================

    window.refreshEvents =
        refreshEvents;


    // =========================================
    // INITIALISE
    // =========================================

    initialiseEventsDropdown();

    initialiseDropdownClose();

    initialiseEventFeatureToggles();

    initialiseOverviewTabs();

    updateEventTimeLeft();


    // =========================================
    // TIMER
    // =========================================

    if (!window.eventsTimerInterval) {

        window.eventsTimerInterval =
            setInterval(
                updateEventTimeLeft,
                1000
            );

    }


    // =========================================
    // AUTOMATIC REFRESH
    // =========================================

    if (!window.eventsRefreshInterval) {

        window.eventsRefreshInterval =
            setInterval(
                refreshEvents,
                60000
            );

    }


    // =========================================
    // REFRESH WHEN TAB BECOMES VISIBLE
    // =========================================

    if (!window.eventsVisibilityInitialised) {

        window.eventsVisibilityInitialised =
            true;


        document.addEventListener(
            "visibilitychange",
            () => {

                if (
                    document.visibilityState ===
                    "visible"
                ) {

                    refreshEvents();

                }

            }
        );

    }

}


window.initEvents =
    initEvents;