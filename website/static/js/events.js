function initEvents() {

    // =========================================
    // PAGE
    // =========================================

    let eventsPage =
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
            event => {

                event.preventDefault();
                event.stopPropagation();

                dropdown.classList.toggle("open");

            }
        );


        // -----------------------------------------
        // Account Options
        // -----------------------------------------

        const options =
            dropdown.querySelectorAll(
                ".custom-select-option"
            );


        options.forEach(option => {

            if (
                option.dataset.initialised ===
                "true"
            ) {
                return;
            }

            option.dataset.initialised = "true";


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


                    // Close immediately.
                    dropdown.classList.remove(
                        "open"
                    );


                    // Navigate to the selected account while
                    // preserving the currently selected category.
                    const currentTab =
                        document.querySelector(
                            ".events-account-tab.active"
                        )?.dataset.accountTab ||
                        localStorage.getItem(
                            "cyreneAccountEventTab"
                        ) ||
                        "all";

                    window.location.href =
                        `/events?account_id=${accountId}&tab=${encodeURIComponent(currentTab)}`;

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
            event => {

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
    // ACCOUNT TABS
    // =========================================

    function initialiseAccountTabs() {

        const page =
            document.querySelector(".events-page");

        if (!page) {
            return;
        }


        const tabs =
            page.querySelectorAll(
                ".events-account-tab"
            );

        const sections =
            page.querySelectorAll(
                "[data-account-category]"
            );

        if (!tabs.length || !sections.length) {
            return;
        }


        // -----------------------------------------
        // Activate Category
        // -----------------------------------------

        function activateCategory(category) {

            tabs.forEach(tab => {

                tab.classList.toggle(
                    "active",
                    tab.dataset.accountTab === category
                );

            });


            sections.forEach(section => {

                const sectionCategory =
                    section.dataset.accountCategory;

                const isEmptyState =
                    section.classList.contains(
                        "events-account-empty"
                    );


                // ---------------------------------
                // ALL
                // ---------------------------------

                if (category === "all") {

                    // Show actual content.
                    // Hide placeholder states.
                    section.hidden =
                        isEmptyState;

                    return;
                }


                // ---------------------------------
                // CATEGORY
                // ---------------------------------

                section.hidden =
                    sectionCategory !== category;

            });


            // Save the selected category so
            // automatic refreshes can restore it.
            localStorage.setItem(
                "cyreneAccountEventTab",
                category
            );

        }


        // -----------------------------------------
        // Listeners
        // -----------------------------------------

        tabs.forEach(tab => {

            if (
                tab.dataset.initialised ===
                "true"
            ) {
                return;
            }

            tab.dataset.initialised = "true";


            tab.addEventListener(
                "click",
                () => {

                    const category =
                        tab.dataset.accountTab;

                    if (!category) {
                        return;
                    }

                    activateCategory(
                        category
                    );

                }
            );

        });


        // -----------------------------------------
        // Restore Previously Selected Category
        // -----------------------------------------

        const urlCategory =
            new URLSearchParams(
                window.location.search
            ).get("tab");

        const savedCategory =
            localStorage.getItem(
                "cyreneAccountEventTab"
            );

        const categoryToActivate =
            urlCategory ||
            savedCategory ||
            "all";

        const categoryExists =
            Array.from(tabs).some(
                tab =>
                    tab.dataset.accountTab ===
                    categoryToActivate
            );

        activateCategory(
            categoryExists
                ? categoryToActivate
                : "all"
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
                    event => {

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

        const page =
            document.querySelector(
                ".events-page"
            );

        if (!page) {
            return;
        }


        const tabs =
            page.querySelectorAll(
                ".events-overview-tab"
            );

        const panels =
            page.querySelectorAll(
                ".events-overview-panel"
            );


        if (!tabs.length || !panels.length) {
            return;
        }


        // -----------------------------------------
        // Activate Overview Tab
        // -----------------------------------------

        function activateTab(target) {

            document.documentElement.dataset.overviewTab =
                target;


            tabs.forEach(tab => {

                tab.classList.toggle(
                    "active",
                    tab.dataset.overviewTab ===
                    target
                );

            });


            panels.forEach(panel => {

                panel.classList.toggle(
                    "active",
                    panel.dataset.overviewPanel ===
                    target
                );

            });

        }


        // -----------------------------------------
        // Listeners
        // -----------------------------------------

        tabs.forEach(tab => {

            if (
                tab.dataset.initialised ===
                "true"
            ) {
                return;
            }

            tab.dataset.initialised = "true";


            tab.addEventListener(
                "click",
                () => {

                    const target =
                        tab.dataset.overviewTab;

                    if (!target) {
                        return;
                    }


                    localStorage.setItem(
                        "cyreneOverviewTab",
                        target
                    );


                    activateTab(
                        target
                    );

                }
            );

        });


        // -----------------------------------------
        // Restore Previously Selected Tab
        // -----------------------------------------

        const savedTab =
            localStorage.getItem(
                "cyreneOverviewTab"
            );


        const savedTabExists =
            Array.from(tabs).some(
                tab =>
                    tab.dataset.overviewTab ===
                    savedTab
            );


        activateTab(
            savedTabExists
                ? savedTab
                : "daily"
        );

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

                let timestamp =
                    Number(
                        timer.dataset.resinTimestamp
                    );

                const currentTime =
                    Math.floor(
                        Date.now() / 1000
                    );


                // -----------------------------------------
                // FULL RESIN
                // -----------------------------------------

                if (!timestamp) {

                    timer.textContent =
                        "Full";

                    return;

                }


                // -----------------------------------------
                // NEXT RESIN
                // -----------------------------------------

                if (
                    timer.dataset.resinKind ===
                    "next" &&
                    timestamp <= currentTime
                ) {

                    // Each Resin takes 8 minutes.
                    while (
                        timestamp <= currentTime
                    ) {

                        timestamp += 480;

                    }

                    timer.dataset.resinTimestamp =
                        String(timestamp);

                }


                const remaining =
                    Math.max(
                        0,
                        timestamp - currentTime
                    );


                const hours =
                    Math.floor(
                        remaining / 3600
                    );

                const minutes =
                    Math.floor(
                        (remaining % 3600) / 60
                    );

                const seconds =
                    remaining % 60;


                if (hours > 0) {

                    timer.textContent =
                        `${hours}h ${minutes}m`;

                } else if (minutes > 0) {

                    timer.textContent =
                        `${minutes}m ${seconds}s`;

                } else {

                    timer.textContent =
                        `${seconds}s`;

                }

            });

    }


    // =========================================
    // ACTIVITY CHECKMARKS
    // =========================================

    function initialiseActivityCheckmarks() {

        document
            .querySelectorAll(
                ".event-checkmark[data-activity-type]"
            )
            .forEach(checkmark => {

                if (
                    checkmark.dataset.initialised ===
                    "true"
                ) {
                    return;
                }

                checkmark.dataset.initialised =
                    "true";


                checkmark.addEventListener(
                    "click",
                    async event => {

                        event.preventDefault();
                        event.stopPropagation();


                        const accountId =
                            checkmark.dataset.accountId;

                        const activityType =
                            checkmark.dataset.activityType;


                        if (
                            !accountId ||
                            !activityType
                        ) {
                            return;
                        }


                        const currentlyChecked =
                            checkmark.getAttribute(
                                "aria-pressed"
                            ) === "true";


                        const newChecked =
                            !currentlyChecked;


                        // Prevent duplicate clicks
                        // while the request is saving.
                        if (
                            checkmark.dataset.saving ===
                            "true"
                        ) {
                            return;
                        }


                        checkmark.dataset.saving =
                            "true";


                        try {

                            const response =
                                await fetch(
                                    "/api/events/activity-check",
                                    {
                                        method: "POST",

                                        headers: {
                                            "Content-Type":
                                                "application/json",
                                        },

                                        body:
                                            JSON.stringify({
                                                account_id:
                                                    Number(
                                                        accountId
                                                    ),

                                                activity_type:
                                                    activityType,

                                                checked:
                                                    newChecked,
                                            }),
                                    }
                                );


                            const responseText =
                                await response.text();


                            let data;


                            try {

                                data =
                                    JSON.parse(
                                        responseText
                                    );

                            } catch {

                                throw new Error(
                                    `Server returned ${response.status}: ${responseText}`
                                );

                            }


                            if (
                                !response.ok ||
                                !data.success
                            ) {

                                throw new Error(
                                    data.error ||
                                    `Failed to save activity check (${response.status}).`
                                );

                            }


                            checkmark.setAttribute(
                                "aria-pressed",
                                String(
                                    data.checked
                                )
                            );


                            checkmark.classList.toggle(
                                "event-checkmark-empty",
                                !data.checked
                            );


                            const row =
                                checkmark.closest(
                                    ".event-list-item"
                                );


                            if (row) {

                                row.classList.toggle(
                                    "completed",
                                    data.checked
                                );

                            }


                        } catch (error) {

                            console.error(
                                "Failed to update activity checkmark:",
                                error
                            );


                        } finally {

                            delete checkmark.dataset.saving;

                        }

                    }
                );

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
            // Current Page State
            // -----------------------------------------

            const isOverview =
                currentPage.dataset.overview ===
                "true";


            const accountId =
                currentPage.dataset.accountId ||
                "";


            // -----------------------------------------
            // Preserve UI State
            // -----------------------------------------

            const expandedCards =
                Array.from(
                    currentPage.querySelectorAll(
                        ".event-featured-card:not(.collapsed)"
                    )
                ).map(
                    card =>
                        card.dataset.eventType
                );


            const activeAccountTab =
                currentPage
                    .querySelector(
                        ".events-account-tab.active"
                    )
                    ?.dataset.accountTab ||
                localStorage.getItem(
                    "cyreneAccountEventTab"
                ) ||
                "all";


            const activeOverviewTab =
                currentPage
                    .querySelector(
                        ".events-overview-tab.active"
                    )
                    ?.dataset.overviewTab ||
                localStorage.getItem(
                    "cyreneOverviewTab"
                ) ||
                "daily";


            const scrollPosition =
                window.scrollY;


            // -----------------------------------------
            // Build Request
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
            // Replace Page
            // -----------------------------------------

            currentPage.replaceWith(
                newPage
            );


            // IMPORTANT:
            // The old eventsPage reference is no
            // longer valid after replaceWith().
            eventsPage =
                document.querySelector(
                    ".events-page"
                );


            if (!eventsPage) {
                return;
            }


            // -----------------------------------------
            // Restore Expanded Cards
            // -----------------------------------------

            expandedCards.forEach(
                eventType => {

                    const card =
                        eventsPage.querySelector(
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
            // Reinitialise Controls
            // -----------------------------------------

            initialiseEventsDropdown();

            initialiseAccountTabs();

            initialiseEventFeatureToggles();

            initialiseOverviewTabs();

            initialiseActivityCheckmarks();

            updateEventTimeLeft();


            // -----------------------------------------
            // Restore Account Category
            // -----------------------------------------

            if (!isOverview) {

                const accountTab =
                    eventsPage.querySelector(
                        `.events-account-tab[data-account-tab="${activeAccountTab}"]`
                    );


                if (accountTab) {

                    accountTab.click();

                }

            }


            // -----------------------------------------
            // Restore Overview Category
            // -----------------------------------------

            if (isOverview) {

                const overviewTab =
                    eventsPage.querySelector(
                        `.events-overview-tab[data-overview-tab="${activeOverviewTab}"]`
                    );


                if (overviewTab) {

                    overviewTab.click();

                }

            }


            // -----------------------------------------
            // Restore Scroll Position
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

    initialiseAccountTabs();

    initialiseEventFeatureToggles();

    initialiseOverviewTabs();

    initialiseActivityCheckmarks();

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