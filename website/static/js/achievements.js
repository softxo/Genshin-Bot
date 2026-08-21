document.addEventListener("DOMContentLoaded", () => {

    const categories = document.getElementById("achievement-categories");
    const browser = document.getElementById("achievement-browser");
    const backButton = document.getElementById("achievement-back");

    const categoryButtons = document.querySelectorAll(
        ".achievement-category"
    );

    const sidebarButtons = document.querySelectorAll(
        ".achievement-sidebar-item"
    );

    const categoryTitle = document.getElementById(
        "achievement-category-title"
    );

    const categoryProgress = document.getElementById(
        "achievement-category-progress"
    );


    const categoryData = {

        wonders: {
            title: "Wonders of the World",
            completed: 24,
            total: 80
        },

        memories: {
            title: "Memories of the Heart",
            completed: 18,
            total: 60
        },

        "the-abyss": {
            title: "The Abyss",
            completed: 12,
            total: 40
        },

        exploration: {
            title: "Exploration",
            completed: 31,
            total: 100
        }

    };


    function openCategory(category) {

        const data = categoryData[category];

        if (!data) {
            return;
        }


        categoryTitle.textContent = data.title;

        categoryProgress.textContent =
            `${data.completed} / ${data.total} completed`;


        sidebarButtons.forEach(button => {

            button.classList.toggle(
                "active",
                button.dataset.category === category
            );

        });


        categories.hidden = true;
        browser.hidden = false;

    }


    function closeBrowser() {

        browser.hidden = true;
        categories.hidden = false;

    }


    categoryButtons.forEach(button => {

        button.addEventListener("click", () => {

            openCategory(button.dataset.category);

        });

    });


    sidebarButtons.forEach(button => {

        button.addEventListener("click", () => {

            openCategory(button.dataset.category);

        });

    });


    if (backButton) {

        backButton.addEventListener("click", () => {

            closeBrowser();

        });

    }

});