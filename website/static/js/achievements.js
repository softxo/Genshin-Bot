document.addEventListener("DOMContentLoaded", () => {

    const categories = document.getElementById(
        "achievement-categories"
    );

    const categoryGrid = document.getElementById(
        "achievement-category-grid"
    );

    const browser = document.getElementById(
        "achievement-browser"
    );

    const backButton = document.getElementById(
        "achievement-back"
    );

    const sidebarList = document.getElementById(
        "achievement-sidebar-list"
    );

    const achievementList = document.getElementById(
        "achievement-list"
    );

    const categoryTitle = document.getElementById(
        "achievement-category-title"
    );

    const categoryProgress = document.getElementById(
        "achievement-category-progress"
    );


    let achievementData = null;


    /*
     * --------------------------------------------------
     * LOAD ACHIEVEMENTS
     * --------------------------------------------------
     */

    async function loadAchievements() {

        try {

            const response = await fetch(
                "/api/achievements"
            );

            if (!response.ok) {
                throw new Error(
                    "Failed to load achievements."
                );
            }

            achievementData = await response.json();

            buildCategories();

        } catch (error) {

            console.error(
                "Failed to load achievements:",
                error
            );

        }

    }


    /*
     * --------------------------------------------------
     * BUILD CATEGORY CARDS
     * --------------------------------------------------
     */

    function buildCategories() {

        if (!categoryGrid || !achievementData) {
            return;
        }


        categoryGrid.innerHTML = "";


        const categoryEntries =
            Object.entries(
                achievementData.categories
            );


        categoryEntries.forEach(
            ([category, data]) => {

                const button =
                    document.createElement("button");

                button.type = "button";

                button.className =
                    "achievement-category";


                const progress =
                    data.total > 0
                        ? (
                            data.completed /
                            data.total
                        ) * 100
                        : 0;


                button.innerHTML = `

                    <div class="achievement-category-icon">

                        <img
                            src="/static/images/Achievements.webp"
                            alt=""
                        >

                    </div>


                    <div class="achievement-category-content">

                        <h3>
                            ${escapeHTML(category)}
                        </h3>

                        <span>
                            ${data.completed} /
                            ${data.total}
                            completed
                        </span>


                        <div
                            class="achievement-category-progress"
                        >

                            <div
                                class="achievement-category-progress-fill"
                                style="width: ${progress}%"
                            ></div>

                        </div>

                    </div>


                    <span
                        class="achievement-category-arrow"
                    >
                        →
                    </span>

                `;


                button.addEventListener(
                    "click",
                    () => {

                        openCategory(category);

                    }
                );


                categoryGrid.appendChild(button);

            }
        );

    }


    /*
     * --------------------------------------------------
     * BUILD SIDEBAR
     * --------------------------------------------------
     */

    function buildSidebar(
        selectedCategory
    ) {

        if (!sidebarList || !achievementData) {
            return;
        }


        sidebarList.innerHTML = "";


        Object.entries(
            achievementData.categories
        ).forEach(
            ([category, data]) => {

                const button =
                    document.createElement("button");

                button.type = "button";

                button.className =
                    "achievement-sidebar-item";


                if (
                    category === selectedCategory
                ) {

                    button.classList.add("active");

                }


                button.innerHTML = `

                    <span>
                        ${escapeHTML(category)}
                    </span>

                    <small>
                        ${data.completed} /
                        ${data.total}
                    </small>

                `;


                button.addEventListener(
                    "click",
                    () => {

                        openCategory(category);

                    }
                );


                sidebarList.appendChild(button);

            }
        );

    }


    /*
     * --------------------------------------------------
     * OPEN CATEGORY
     * --------------------------------------------------
     */

    function openCategory(category) {

        if (!achievementData) {
            return;
        }


        const data =
            achievementData.categories[category];


        if (!data) {
            return;
        }


        categoryTitle.textContent =
            category;


        categoryProgress.textContent =
            `${data.completed} / ${data.total} completed`;


        buildSidebar(category);

        buildAchievements(category);


        categories.hidden = true;

        browser.hidden = false;

    }


    /*
     * --------------------------------------------------
     * BUILD ACHIEVEMENTS
     * --------------------------------------------------
     */

    function buildAchievements(category) {

        if (
            !achievementList ||
            !achievementData
        ) {
            return;
        }


        achievementList.innerHTML = "";


        const achievements =
            achievementData.achievements.filter(
                achievement =>
                    achievement.category === category
            );


        achievements.forEach(
            achievement => {

                const item =
                    document.createElement("div");

                item.className =
                    "achievement-item";


                const totalTiers =
                    achievement.tiers?.length || 1;

                const currentTier = 0;


                item.innerHTML = `
    
                    <div class="achievement-item-tier">
    
                        <img
                            src="${getTierImage(
                                currentTier,
                                totalTiers
                            )}"
                            alt="${currentTier}/${totalTiers}"
                        >
    
                    </div>
    
    
                    <div class="achievement-item-content">
    
                        <h3>
                            ${escapeHTML(
                                achievement.name
                            )}
                        </h3>
    
                        <p>
                            ${getAchievementDescription(
                                achievement
                            )}
                        </p>
    
                    </div>
    
    
                    <button
                        type="button"
                        class="achievement-complete-button"
                        aria-label="Mark ${escapeHTML(
                            achievement.name
                        )} completed"
                        title="Mark Completed"
                    >
                    </button>
    
                `;


                const completeButton =
                    item.querySelector(
                        ".achievement-complete-button"
                    );


                completeButton.addEventListener(
                    "click",
                    () => {

                        markCompleted(
                            achievement,
                            item
                        );

                    }
                );


                achievementList.appendChild(item);

            }
        );

    }

    function getTierImage(
        currentTier,
        totalTiers
    ) {

        return `/static/images/achievements/tiers/Achievement_${currentTier}_${totalTiers}.png`;

    }


    /*
     * --------------------------------------------------
     * ACHIEVEMENT DESCRIPTION
     * --------------------------------------------------
     */

    function getAchievementDescription(
        achievement
    ) {

        if (
            !achievement.tiers ||
            achievement.tiers.length === 0
        ) {

            return "";

        }


        if (
            achievement.tiers.length === 1
        ) {

            return escapeHTML(
                achievement.tiers[0].description
            );

        }


        return achievement.tiers
            .map(tier => {

                return `
                    Tier ${tier.tier}:
                    ${escapeHTML(
                        tier.description
                    )}
                `;

            })
            .join("<br>");

    }


    /*
     * --------------------------------------------------
     * MARK COMPLETED
     * --------------------------------------------------
     *
     * TEMPORARY FRONT-END STATE.
     */

    function markCompleted(
        achievement,
        item
    ) {

        item.classList.add("completed");


        const totalTiers =
            achievement.tiers?.length || 1;


        const tier =
            item.querySelector(
                ".achievement-item-tier img"
            );


        if (tier) {

            tier.src =
                getTierImage(
                    totalTiers,
                    totalTiers
                );

            tier.alt =
                `${totalTiers}/${totalTiers}`;

        }


        const button =
            item.querySelector(
                ".achievement-complete-button"
            );


        button.classList.add("completed");

        button.disabled = true;

        button.title =
            "Completed";

    }


    /*
     * --------------------------------------------------
     * BACK TO CATEGORIES
     * --------------------------------------------------
     */

    function closeBrowser() {

        browser.hidden = true;

        categories.hidden = false;

    }


    if (backButton) {

        backButton.addEventListener(
            "click",
            closeBrowser
        );

    }


    /*
     * --------------------------------------------------
     * HTML ESCAPING
     * --------------------------------------------------
     *
     * Prevents achievement/category data
     * from being interpreted as HTML.
     */

    function escapeHTML(value) {

        const div =
            document.createElement("div");

        div.textContent =
            value ?? "";

        return div.innerHTML;

    }


    /*
     * --------------------------------------------------
     * INITIAL LOAD
     * --------------------------------------------------
     */

    loadAchievements();

});