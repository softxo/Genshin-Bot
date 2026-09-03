function initEvents() {

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


    async function refreshDailyCommissions(timer) {

        const container =
            document.getElementById(
                "daily-commissions"
            );

        if (!container) {
            return;
        }

        const accountId =
            container.dataset.accountId;

        if (!accountId) {
            return;
        }

        try {

            const response =
                await fetch(
                    `/api/events/daily?account_id=${accountId}`,
                    {
                        credentials: "same-origin"
                    }
                );

            if (!response.ok) {
                return;
            }

            const data =
                await response.json();

            if (!data.success) {
                return;
            }


            /*
             * Update the timer with the
             * new server-generated reset time.
             */

            timer.dataset.endTime =
                String(data.reset_time);


            /*
             * Update completion status.
             */

            const status =
                document.getElementById(
                    "daily-commissions-status"
                );

            const check =
                document.getElementById(
                    "daily-commissions-check"
                );


            const completed =
                Number(data.completed);

            const total =
                Number(data.total);

            const claimed =
                Boolean(data.claimed_reward);

            const fullyCompleted =
                completed >= total &&
                claimed;


            if (status) {

                status.classList.remove(
                    "claimed",
                    "not-claimed"
                );


                if (completed >= total) {

                    if (claimed) {

                        status.textContent =
                            "Claimed";

                        status.classList.add(
                            "claimed"
                        );

                    } else {

                        status.textContent =
                            "Not Claimed";

                        status.classList.add(
                            "not-claimed"
                        );

                    }

                } else {

                    status.textContent =
                        `${completed} / ${total}`;

                }

            }


            /*
             * Update the checkmark.
             */

            if (check) {

                check.classList.toggle(
                    "event-checkmark-empty",
                    !fullyCompleted
                );

            }


            /*
             * Update the completed card state.
             */

            container.classList.toggle(
                "completed",
                fullyCompleted
            );

        } catch (error) {

            console.error(
                "Failed to refresh Daily Commissions:",
                error
            );

        }

    }


    function updateEventTimeLeft() {

        const timers =
            document.querySelectorAll(
                ".event-time-left[data-end-time]"
            );

        const now =
            Math.floor(Date.now() / 1000);

        timers.forEach(timer => {

            const endTime =
                Number(timer.dataset.endTime);

            const remaining =
                endTime - now;


            /*
             * Recurring Daily Commissions.
             *
             * Do not display "Ended".
             * Fetch the new state from the server.
             */

            if (
                remaining <= 0 &&
                timer.classList.contains(
                    "event-daily-reset"
                )
            ) {

                if (
                    !timer.dataset.refreshing
                ) {

                    timer.dataset.refreshing =
                        "true";

                    timer.textContent =
                        "Updating...";

                    refreshDailyCommissions(
                        timer
                    ).finally(() => {

                        delete timer.dataset.refreshing;

                    });

                }

                return;
            }


            /*
             * Non-recurring events genuinely end.
             */

            if (remaining <= 0) {

                timer.textContent =
                    "Ended";

                timer.classList.remove(
                    "warning"
                );

                timer.classList.add(
                    "danger"
                );

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


    initialiseEventsDropdown();

    initialiseEventFeatureToggles();

    updateEventTimeLeft();


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

}


window.initEvents = initEvents;