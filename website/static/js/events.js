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

            if (remaining <= 0) {

                timer.textContent = "Ended";

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


            if (timer.classList.contains("event-daily-reset")) {

                if (remaining < 14400) {
                    timer.classList.add("danger");
                } else if (remaining < 54000) {
                    timer.classList.add("warning");
                }

            } else {

                if (remaining < 86400) {
                    timer.classList.add("danger");
                } else if (remaining < 259200) {
                    timer.classList.add("warning");
                }

            }

            const dailyItem =
                timer.closest(".event-daily-item");

            if (dailyItem) {

                dailyItem.classList.remove(
                    "warning",
                    "danger"
                );

                if (remaining < 14400) {
                    dailyItem.classList.add("danger");
                } else if (remaining < 54000) {
                    dailyItem.classList.add("warning");
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
            60000
        );

}


window.initEvents = initEvents;