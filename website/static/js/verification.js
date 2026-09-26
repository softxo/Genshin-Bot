window.initVerify = function () {

    const verificationData =
        document.getElementById(
            "verification-data"
        );

    const verificationCode =
        document.getElementById(
            "verification-code"
        );

    const verificationStatus =
        document.getElementById(
            "verification-status"
        );


    if (
        !verificationData ||
        !verificationCode ||
        !verificationStatus
    ) {

        console.error(
            "Verification page elements not found."
        );

        return;
    }


    const nextUrl =
        verificationData.dataset.next;


    let verificationToken = null;
    let polling = null;


    async function createVerification() {

        try {

            verificationStatus.textContent =
                "Generating verification code...";


            const response =
                await fetch(
                    "/api/verify/create",
                    {
                        method: "POST"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Failed to create verification request: ${response.status}`
                );

            }


            const data =
                await response.json();


            verificationToken =
                data.token;


            verificationCode.textContent =
                data.code;


            verificationStatus.textContent =
                "Awaiting Verification";


            startPolling();


        } catch (error) {

            console.error(
                "Verification creation failed:",
                error
            );


            verificationStatus.textContent =
                "Unable to start verification.";

        }

    }


    function startPolling() {

        if (polling) {

            clearInterval(
                polling
            );

        }


        polling =
            setInterval(
                checkVerification,
                2000
            );


        checkVerification();

    }


    async function checkVerification() {

        if (!verificationToken) {
            return;
        }


        try {

            const response =
                await fetch(
                    `/api/verify/status?token=${
                        encodeURIComponent(
                            verificationToken
                        )
                    }`
                );


            if (
                response.status === 404
            ) {

                clearInterval(
                    polling
                );

                polling = null;


                verificationStatus.textContent =
                    "This verification request has expired. Please refresh the page.";

                return;

            }


            if (!response.ok) {
                return;
            }


            const data =
                await response.json();


            if (!data.verified) {
                return;
            }


            clearInterval(
                polling
            );

            polling = null;


            verificationStatus.textContent =
                "Successfully connected to Discord.";


            setTimeout(() => {

                window.location.href =
                    nextUrl;

            }, 800);


        } catch (error) {

            console.error(
                "Verification polling failed:",
                error
            );

        }

    }


    createVerification();

};