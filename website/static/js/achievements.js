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

    const categoryPercent = document.getElementById(
        "achievement-category-percent"
    );

    const categoryProgressFill = document.getElementById(
        "achievement-category-progress-fill"
    );

    let achievementData = null;

    const CATEGORY_ICONS = {

        "Wonders of the World":
            "/static/images/achievements/categories/Wonders_of_the_World.png",

        "Memories of the Heart":
            "/static/images/achievements/categories/Memories_of_the_Heart.png",

        "Mortal Travails: Series I":
            "/static/images/achievements/categories/Mortal_Travails_Series_I.png",

        "Mortal Travails: Series II":
            "/static/images/achievements/categories/Mortal_Travails_Series_II.png",

        "Mortal Travails: Series III":
            "/static/images/achievements/categories/Mortal_Travails_Series_III.png",

        "Mortal Travails: Series IV":
            "/static/images/achievements/categories/Mortal_Travails_Series_IV.png",

        "Mortal Travails: Series V":
            "/static/images/achievements/categories/Mortal_Travails_Series_V.png",

        "Mortal Travails: Series VI":
            "/static/images/achievements/categories/Mortal_Travails_Series_VI.png",

        "Mortal Travails: Series VII":
            "/static/images/achievements/categories/Mortal_Travails_Series_VII.png",

        "The Art of Adventure":
            "/static/images/achievements/categories/The_Art_of_Adventure.png",

        "The Hero's Journey":
            "/static/images/achievements/categories/The_Heros_Journey.png",

        "Mondstadt: The City of Wind and Song":
            "/static/images/achievements/categories/Mondstadt_The_City_of_Wind_and_Song.png",

        "Liyue: The Harbor of Stone and Contracts":
            "/static/images/achievements/categories/Liyue_The_Harbor_of_Stone_and_Contracts.png",

        "Elemental Specialist: Series I":
            "/static/images/achievements/categories/Elemental_Specialist_Series_I.png",

        "Elemental Specialist: Series II":
            "/static/images/achievements/categories/Elemental_Specialist_Series_II.png",

        "Marksmanship":
            "/static/images/achievements/categories/Marksmanship.png",

        "Challenger: Series I":
            "/static/images/achievements/categories/Challenger_Series_I.png",

        "Challenger: Series II":
            "/static/images/achievements/categories/Challenger_Series_II.png",

        "Challenger: Series III":
            "/static/images/achievements/categories/Challenger_Series_III.png",

        "Challenger: Series IV":
            "/static/images/achievements/categories/Challenger_Series_IV.png",

        "Challenger: Series V":
            "/static/images/achievements/categories/Challenger_Series_V.png",

        "Challenger: Series VI":
            "/static/images/achievements/categories/Challenger_Series_VI.png",

        "Challenger: Series VII":
            "/static/images/achievements/categories/Challenger_Series_VII.png",

        "Challenger: Series VIII":
            "/static/images/achievements/categories/Challenger_Series_VIII.png",

        "Challenger: Series IX":
            "/static/images/achievements/categories/Challenger_Series_IX.png",

        "Challenger: Series X":
            "/static/images/achievements/categories/Challenger_Series_X.png",

        "Domains and Spiral Abyss: Series I":
            "/static/images/achievements/categories/Domains_and_Spiral_Abyss_Series_I.png",

        "Olah!: Series I":
            "/static/images/achievements/categories/Olah!_Series_I.png",

        "Snezhnaya Does Not Believe in Tears: Series I":
            "/static/images/achievements/categories/Snezhnaya_Does_Not_Believe_in_Tears_Series_I.png",

        "Stone Harbor's Nostalgia: Series I":
            "/static/images/achievements/categories/Stone_Harbors_Nostalgia_Series_I.png",

        "Meetings in Outrealm: Series I":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_I.png",

        "Meetings in Outrealm: Series II":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_II.png",

        "Meetings in Outrealm: Series III":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_III.png",

        "Meetings in Outrealm: Series IV":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_IV.png",

        "Meetings in Outrealm: Series V":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_V.png",

        "Meetings in Outrealm: Series VI":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_VI.png",

        "Meetings in Outrealm: Series VII":
            "/static/images/achievements/categories/Meetings_in_Outrealm_Series_VII.png",

        "Visitors on the Icy Mountain":
            "/static/images/achievements/categories/Visitors_on_the_Icy_Mountain.png",

        "A Realm Beyond: Series I":
            "/static/images/achievements/categories/A_Realm_Beyond_Series_I.png",

        "A Realm Beyond: Series II":
            "/static/images/achievements/categories/A_Realm_Beyond_Series_II.png",

        "Inazuma: The Islands of Thunder and Eternity - Series I":
            "/static/images/achievements/categories/Inazuma_The_Islands_of_Thunder_and_Eternity_Series_I.png",

        "Inazuma: The Islands of Thunder and Eternity - Series II":
            "/static/images/achievements/categories/Inazuma_The_Islands_of_Thunder_and_Eternity_Series_II.png",

        "Inazuma: The Islands of Thunder and Eternity - Series III":
            "/static/images/achievements/categories/Inazuma_The_Islands_of_Thunder_and_Eternity_Series_III.png",

        "Teyvat Fishing Guide: Series I":
            "/static/images/achievements/categories/Teyvat_Fishing_Guide_Series_I.png",

        "The Light of Day":
            "/static/images/achievements/categories/The_Light_of_Day.png",

        "Chasmlighter":
            "/static/images/achievements/categories/Chasmlighter.png",

        "Sumeru: The Rainforest of Lore":
            "/static/images/achievements/categories/Sumeru_The_Rainforest_of_Lore.png",

        "Sumeru: The Gilded Desert - Series I":
            "/static/images/achievements/categories/Sumeru_The_Gilded_Desert_Series_I.png",

        "Sumeru: The Gilded Desert - Series II":
            "/static/images/achievements/categories/Sumeru_The_Gilded_Desert_Series_II.png",

        "Genius Invokation TCG":
            "/static/images/achievements/categories/Genius_Invokation_TCG.png",

        "Blessed Hamada":
            "/static/images/achievements/categories/Blessed_Hamada.png",

        "Fontaine: Dance of the Dew-White Springs (I)":
            "/static/images/achievements/categories/Fontaine_Dance_of_the_Dew_White_Springs_I.png",

        "Fontaine: Dance of the Dew-White Springs (II)":
            "/static/images/achievements/categories/Fontaine_Dance_of_the_Dew_White_Springs_II.png",

        "Fontaine: Dance of the Dew-White Springs (III)":
            "/static/images/achievements/categories/Fontaine_Dance_of_the_Dew_White_Springs_III.png",

        "Chenyu's Splendor":
            "/static/images/achievements/categories/Chenyus_Splendor.png",

        "Rhapsodia in the Ancient Sea":
            "/static/images/achievements/categories/Rhapsodia_in_the_Ancient_Sea.png",

        "Imaginarium Theater: The First Folio":
            "/static/images/achievements/categories/Imaginarium_Theater_The_First_Folio.png",

        "Imaginarium Theater: The Second Folio":
            "/static/images/achievements/categories/Imaginarium_Theater_The_Second_Folio.png",

        "Natlan: The Land of Fire and Competition (I)":
            "/static/images/achievements/categories/Natlan_The_Land_of_Fire_and_Competition_I.png",

        "Natlan: The Land of Fire and Competition (II)":
            "/static/images/achievements/categories/Natlan_The_Land_of_Fire_and_Competition_II.png",

        "Duelist: Series I":
            "/static/images/achievements/categories/Duelist_Series_I.png",

        "Duelist: Series II":
            "/static/images/achievements/categories/Duelist_Series_II.png",

        "Duelist: Series III":
            "/static/images/achievements/categories/Duelist_Series_III.png",

        "Repertoire of Myriad Melodies":
            "/static/images/achievements/categories/Reperoire_of_Myriad_Melodies.png",

        "Sacred Mountain's Fading Glow":
            "/static/images/achievements/categories/Sacred_Mountains_Fading_Glow.png",

        "A Summer of Ash and Prickly Pears":
            "/static/images/achievements/categories/A_Summer_of_Ash_and_Prickly_Pears.png",

        "Nod-Krai: An Elysium of Moonlight and Wanderings (I)":
            "/static/images/achievements/categories/Nod_Krai_An_Elysium_of_Moonlight_and_Wanderings_I.png",

        "Nod-Krai: An Elysium of Moonlight and Wanderings (II)":
            "/static/images/achievements/categories/Nod_Krai_An_Elysium_of_Moonlight_and_Wanderings_II.png",

        "Demon Mountain's Breath":
            "/static/images/achievements/categories/Demon_Mountains_Breath.png",

        "Unfettered Crescent":
            "/static/images/achievements/categories/Unfettered_Crescent.png",

        "Snezhnaya: Sacred city of ice and pale star (I)":
            "/static/images/achievements/categories/Snezhnaya_Sacred_city_of_ice_and_pale_star_I.png",

        "Land of Surging Shadows":
            "/static/images/achievements/categories/Land_of_Surging_Shadows.png",

    };

    const CATEGORY_SIDEBAR_ICONS = {

        "Wonders of the World":
            "/static/images/achievements/categories/sidebar/Wonders_of_the_World.png",

        "Memories of the Heart":
            "/static/images/achievements/categories/sidebar/Memories_of_the_Heart.png",

        "Mortal Travails: Series I":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series II":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series III":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series IV":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series V":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series VI":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "Mortal Travails: Series VII":
            "/static/images/achievements/categories/sidebar/Mortal_Travails.png",

        "The Art of Adventure":
            "/static/images/achievements/categories/sidebar/The_Art_of_Adventure.png",

        "The Hero's Journey":
            "/static/images/achievements/categories/sidebar/The_Heros_Journey.png",

        "Mondstadt: The City of Wind and Song":
            "/static/images/achievements/categories/sidebar/Mondstadt_The_City_of_Wind_and_Song.png",

        "Liyue: The Harbor of Stone and Contracts":
            "/static/images/achievements/categories/sidebar/Liyue_The_Harbor_of_Stone_and_Contracts.png",

        "Elemental Specialist: Series I":
            "/static/images/achievements/categories/sidebar/Elemental_Specialist_Series_I.png",

        "Elemental Specialist: Series II":
            "/static/images/achievements/categories/sidebar/Elemental_Specialist_Series_II.png",

        "Marksmanship":
            "/static/images/achievements/categories/sidebar/Marksmanship.png",

        "Challenger: Series I":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series II":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series III":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series IV":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series V":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series VI":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series VII":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series VIII":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series IX":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Challenger: Series X":
            "/static/images/achievements/categories/sidebar/Challenger.png",

        "Domains and Spiral Abyss: Series I":
            "/static/images/achievements/categories/sidebar/Domains_and_Spiral_Abyss_Series_I.png",

        "Olah!: Series I":
            "/static/images/achievements/categories/sidebar/Olah!_Series_I.png",

        "Snezhnaya Does Not Believe in Tears: Series I":
            "/static/images/achievements/categories/sidebar/Snezhnaya_Does_Not_Believe_in_Tears_Series_I.png",

        "Stone Harbor's Nostalgia: Series I":
            "/static/images/achievements/categories/sidebar/Stone_Harbors_Nostalgia_Series_I.png",

        "Meetings in Outrealm: Series I":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series II":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series III":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series IV":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series V":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series VI":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Meetings in Outrealm: Series VII":
            "/static/images/achievements/categories/sidebar/Meetings_in_Outrealm.png",

        "Visitors on the Icy Mountain":
            "/static/images/achievements/categories/sidebar/Visitors_on_the_Icy_Mountain.png",

        "A Realm Beyond: Series I":
            "/static/images/achievements/categories/sidebar/A_Realm_Beyond.png",

        "A Realm Beyond: Series II":
            "/static/images/achievements/categories/sidebar/A_Realm_Beyond.png",

        "Inazuma: The Islands of Thunder and Eternity - Series I":
            "/static/images/achievements/categories/sidebar/Inazuma_The_Islands_of_Thunder_and_Eternity.png",

        "Inazuma: The Islands of Thunder and Eternity - Series II":
            "/static/images/achievements/categories/sidebar/Inazuma_The_Islands_of_Thunder_and_Eternity.png",

        "Inazuma: The Islands of Thunder and Eternity - Series III":
            "/static/images/achievements/categories/sidebar/Inazuma_The_Islands_of_Thunder_and_Eternity.png",

        "Teyvat Fishing Guide: Series I":
            "/static/images/achievements/categories/sidebar/Teyvat_Fishing_Guide_Series_I.png",

        "The Light of Day":
            "/static/images/achievements/categories/sidebar/The_Light_of_Day.png",

        "Chasmlighter":
            "/static/images/achievements/categories/sidebar/Chasmlighter.png",

        "Sumeru: The Rainforest of Lore":
            "/static/images/achievements/categories/sidebar/Sumeru_The_Rainforest_of_Lore.png",

        "Sumeru: The Gilded Desert - Series I":
            "/static/images/achievements/categories/sidebar/Sumeru_The_Gilded_Desert.png",

        "Sumeru: The Gilded Desert - Series II":
            "/static/images/achievements/categories/sidebar/Sumeru_The_Gilded_Desert.png",

        "Genius Invokation TCG":
            "/static/images/achievements/categories/sidebar/Genius_Invokation_TCG.png",

        "Blessed Hamada":
            "/static/images/achievements/categories/sidebar/Blessed_Hamada.png",

        "Fontaine: Dance of the Dew-White Springs (I)":
            "/static/images/achievements/categories/sidebar/Fontaine_Dance_of_the_Dew_White_Springs.png",

        "Fontaine: Dance of the Dew-White Springs (II)":
            "/static/images/achievements/categories/sidebar/Fontaine_Dance_of_the_Dew_White_Springs.png",

        "Fontaine: Dance of the Dew-White Springs (III)":
            "/static/images/achievements/categories/sidebar/Fontaine_Dance_of_the_Dew_White_Springs.png",

        "Chenyu's Splendor":
            "/static/images/achievements/categories/sidebar/Chenyus_Splendor.png",

        "Rhapsodia in the Ancient Sea":
            "/static/images/achievements/categories/sidebar/Rhapsodia_in_the_Ancient_Sea.png",

        "Imaginarium Theater: The First Folio":
            "/static/images/achievements/categories/sidebar/Imaginarium_Theater.png",

        "Imaginarium Theater: The Second Folio":
            "/static/images/achievements/categories/sidebar/Imaginarium_Theater.png",

        "Natlan: The Land of Fire and Competition (I)":
            "/static/images/achievements/categories/sidebar/Natlan_The_Land_of_Fire_and_Competition.png",

        "Natlan: The Land of Fire and Competition (II)":
            "/static/images/achievements/categories/sidebar/Natlan_The_Land_of_Fire_and_Competition.png",

        "Duelist: Series I":
            "/static/images/achievements/categories/sidebar/Duelist.png",

        "Duelist: Series II":
            "/static/images/achievements/categories/sidebar/Duelist.png",

        "Duelist: Series III":
            "/static/images/achievements/categories/sidebar/Duelist.png",

        "Repertoire of Myriad Melodies":
            "/static/images/achievements/categories/sidebar/Reperoire_of_Myriad_Melodies.png",

        "Sacred Mountain's Fading Glow":
            "/static/images/achievements/categories/sidebar/Sacred_Mountains_Fading_Glow.png",

        "A Summer of Ash and Prickly Pears":
            "/static/images/achievements/categories/sidebar/A_Summer_of_Ash_and_Prickly_Pears.png",

        "Nod-Krai: An Elysium of Moonlight and Wanderings (I)":
            "/static/images/achievements/categories/sidebar/Nod_Krai_An_Elysium_of_Moonlight_and_Wanderings.png",

        "Nod-Krai: An Elysium of Moonlight and Wanderings (II)":
            "/static/images/achievements/categories/sidebar/Nod_Krai_An_Elysium_of_Moonlight_and_Wanderings.png",

        "Demon Mountain's Breath":
            "/static/images/achievements/categories/sidebar/Demon_Mountains_Breath.png",

        "Unfettered Crescent":
            "/static/images/achievements/categories/sidebar/Unfettered_Crescent.png",

        "Snezhnaya: Sacred city of ice and pale star (I)":
            "/static/images/achievements/categories/sidebar/Snezhnaya_Sacred_city_of_ice_and_pale_star.png",

        "Land of Surging Shadows":
            "/static/images/achievements/categories/sidebar/Land_of_Surging_Shadows.png",

    };


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
            updateOverallAchievementProgress();

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
                            src="${CATEGORY_ICONS[category] || "/static/images/Achievements.webp"}"
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

                    <div class="achievement-sidebar-icon">
                
                        <img
                            src="${
                                CATEGORY_SIDEBAR_ICONS[category]
                                || "/static/images/Achievements.webp"
                            }"
                            alt=""
                        >
                
                    </div>
                
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

        console.log("Opened category:", category);
        console.log("Category data:", data);


        if (!data) {
            return;
        }


        categoryTitle.textContent =
            category;


        const percentage =
            data.total > 0
                ? (data.completed / data.total) * 100
                : 0;


        const roundedPercentage =
            Math.round(percentage * 10) / 10;


        categoryPercent.textContent =
            `${roundedPercentage}% (${data.completed}/${data.total})`;


        categoryProgressFill.style.width =
            `${percentage}%`;


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


                item.innerHTML = `
    
                    <!-- Large achievement icon -->
    
                    <div class="achievement-item-icon">
    
                        <img
                            class="achievement-item-main-icon"
                            src="${getTierImage(
                                0,
                                totalTiers
                            )}"
                            alt=""
                        >
    
                    </div>
    
    
                    <!-- Achievement content -->
    
                    <div class="achievement-item-content">
    
                        <div class="achievement-item-header">
    
                            <h3>
                                ${escapeHTML(
                                    achievement.name
                                )}
                            </h3>
    
                        </div>
    
    
                        <div class="achievement-tier-list">
    
                            ${achievement.tiers.map(
                                tier => {
    
                                    return `
    
                                        <div
                                            class="achievement-tier ${
                                                tier.completed ? "completed" : ""
                                            }"
                                            data-tier="${tier.tier}"
                                        >
    
                                            <!-- Small tier icon -->
    
                                            <div class="achievement-tier-icon">
    
                                                <img
                                                    src="${getTierImage(
                                                        tier.tier,
                                                        totalTiers
                                                    )}"
                                                    alt="${tier.tier}/${totalTiers}"
                                                >
    
                                            </div>
    
    
                                            <div class="achievement-tier-content">
    
                                                <p>
                                                    ${escapeHTML(
                                                        tier.description
                                                    )}
                                                </p>
    
                                            </div>
    
    
                                            <button
                                                type="button"
                                                class="achievement-complete-button ${
                                                    tier.completed ? "completed" : ""
                                                }"
                                                aria-label="Mark tier ${tier.tier} completed"
                                                title="${
                                                    tier.completed
                                                        ? "Mark Incomplete"
                                                        : "Mark Completed"
                                                }"
                                            >
                                            </button>
    
                                        </div>
    
                                    `;
    
                                }
                            ).join("")}
    
                        </div>
    
                    </div>
    
                `;


                const tierButtons =
                    item.querySelectorAll(
                        ".achievement-complete-button"
                    );


                tierButtons.forEach(
                    (button, index) => {

                        const tier =
                            achievement.tiers[index];


                        button.addEventListener(
                            "click",
                            () => {

                                toggleTierCompleted(
                                    achievement,
                                    tier,
                                    item,
                                    button
                                );

                            }
                        );

                    }
                );


                updateTierAvailability(item);


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

    function getAchievementDescription(achievement) {

        if (
            !achievement.tiers ||
            achievement.tiers.length === 0
        ) {
            return "";
        }


        const totalTiers =
            achievement.tiers.length;


        return achievement.tiers
            .map(tier => {

                const tierNumber =
                    tier.tier;


                return `
                    <div class="achievement-tier-row">
    
                        <img
                            src="${getTierImage(
                                tierNumber,
                                totalTiers
                            )}"
                            alt="${tierNumber}/${totalTiers}"
                        >
    
                        <span>
                            ${escapeHTML(
                                tier.description
                            )}
                        </span>
    
                    </div>
                `;

            })
            .join("");

    }


    /*
     * --------------------------------------------------
     * MARK COMPLETED
     * --------------------------------------------------
     */

    function toggleTierCompleted(
        achievement,
        tier,
        item,
        button
    ) {

        const totalTiers =
            achievement.tiers?.length || 1;


        const tierContainer =
            button.closest(
                ".achievement-tier"
            );


        const tierImage =
            tierContainer.querySelector(
                ".achievement-tier-icon img"
            );


        const isCompleted =
            tierContainer.classList.contains(
                "completed"
            );


        /*
         * ------------------------------------------
         * TOGGLE CURRENT TIER
         * ------------------------------------------
         */

        if (isCompleted) {

            /*
             * Uncompleting a tier also uncompletes
             * every tier after it.
             */

            achievement.tiers.forEach(
                achievementTier => {

                    if (
                        achievementTier.tier >= tier.tier
                    ) {

                        achievementTier.completed = false;

                    }

                }
            );


            /*
             * Update the clicked tier visually.
             */

            tierContainer.classList.remove(
                "completed"
            );

            button.classList.remove(
                "completed"
            );

            tierImage.src =
                getTierImage(
                    tier.tier,
                    totalTiers
                );

            tierImage.alt =
                `${tier.tier}/${totalTiers}`;

            button.title =
                "Mark Completed";

        } else {

            tierContainer.classList.add(
                "completed"
            );

            button.classList.add(
                "completed"
            );

            tierImage.src =
                getTierImage(
                    tier.tier,
                    totalTiers
                );

            tierImage.alt =
                `${tier.tier}/${totalTiers}`;

            button.title =
                "Mark Incomplete";

            tier.completed = true;

        }


        /*
         * ------------------------------------------
         * CHECK WHETHER ENTIRE ACHIEVEMENT
         * IS COMPLETED
         * ------------------------------------------
         */

        const tierContainers =
            item.querySelectorAll(
                ".achievement-tier"
            );


        const completedTiers =
            item.querySelectorAll(
                ".achievement-tier.completed"
            );


        const achievementCompleted =
            completedTiers.length ===
            tierContainers.length;


        /*
         * ------------------------------------------
         * UPDATE ACHIEVEMENT BOX
         * ------------------------------------------
         */

        item.classList.toggle(
            "completed",
            achievementCompleted
        );


        /*
         * ------------------------------------------
         * UPDATE LARGE ICON
         * ------------------------------------------
         */

        const largeIcon =
            item.querySelector(
                ".achievement-item-icon img"
            );


        if (largeIcon) {

            let highestCompletedTier = 0;


            completedTiers.forEach(
                completedTier => {

                    const tierNumber =
                        Number(
                            completedTier.dataset.tier
                        );


                    if (
                        tierNumber >
                        highestCompletedTier
                    ) {

                        highestCompletedTier =
                            tierNumber;

                    }

                }
            );


            largeIcon.src =
                getTierImage(
                    highestCompletedTier,
                    totalTiers
                );


            largeIcon.alt =
                `${highestCompletedTier}/${totalTiers}`;

        }

        updateLockedTiers(item);
        updateAchievementProgress(item);

        updateCategoryProgress();
        updateOverallAchievementProgress();
    }

    function updateAchievementProgress(item) {

        const tiers =
            item.querySelectorAll(
                ".achievement-tier"
            );


        const completedTiers =
            item.querySelectorAll(
                ".achievement-tier.completed"
            );


        const totalTiers =
            tiers.length;


        const completedCount =
            completedTiers.length;


        /*
         * Remove previous progress states.
         */

        item.classList.remove(
            "progress-low",
            "progress-high"
        );


        /*
         * Force the browser to register
         * the class removal so the animation
         * can restart when the new class is added.
         */

        void item.offsetWidth;


        /*
         * Do not apply progress colour
         * to a fully completed achievement.
         */

        if (
            totalTiers === 0 ||
            completedCount === totalTiers
        ) {
            return;
        }


        const progress =
            completedCount / totalTiers;


        /*
         * 1/3 complete.
         */

        if (
            progress >= 1 / 3 &&
            progress < 1 / 2
        ) {

            item.classList.add(
                "progress-low"
            );

        }


        /*
         * 1/2 complete or more,
         * but not fully completed.
         */

        else if (
            progress >= 1 / 2
        ) {

            item.classList.add(
                "progress-high"
            );

        }

    }

    function updateCategoryProgress() {

        if (!achievementData) {
            return;
        }


        /*
         * Recalculate every category from the
         * current tier completion state.
         */

        Object.entries(
            achievementData.categories
        ).forEach(
            ([category, data]) => {

                let completed = 0;


                achievementData.achievements.forEach(
                    achievement => {

                        if (
                            achievement.category !== category ||
                            !Array.isArray(
                                achievement.tiers
                            )
                        ) {
                            return;
                        }


                        achievement.tiers.forEach(
                            tier => {

                                if (
                                    tier.completed === true
                                ) {

                                    completed++;

                                }

                            }
                        );

                    }
                );


                data.completed = completed;

            }
        );


        /*
         * Rebuild the category cards.
         */

        buildCategories();


        /*
         * Rebuild the sidebar if we are currently
         * inside a category.
         */

        if (
            browser &&
            !browser.hidden &&
            categoryTitle
        ) {

            buildSidebar(
                categoryTitle.textContent
            );

        }

    }

    function updateLockedTiers(item) {

        const tiers =
            item.querySelectorAll(
                ".achievement-tier"
            );

        let previousCompleted = true;


        tiers.forEach(
            tier => {

                const button =
                    tier.querySelector(
                        ".achievement-complete-button"
                    );


                if (previousCompleted) {

                    tier.classList.remove(
                        "locked"
                    );

                    button.disabled = false;

                } else {

                    /*
                     * A tier cannot be completed until
                     * the previous tier is completed.
                     */

                    tier.classList.add(
                        "locked"
                    );

                    tier.classList.remove(
                        "completed"
                    );

                    button.classList.remove(
                        "completed"
                    );

                    button.disabled = true;

                    button.title =
                        "Complete the previous tier first";

                }


                previousCompleted =
                    tier.classList.contains(
                        "completed"
                    );

            }
        );


        /*
         * ------------------------------------------
         * UPDATE LARGE ACHIEVEMENT ICON
         * ------------------------------------------
         */

        const mainIcon =
            item.querySelector(
                ".achievement-item-main-icon"
            );


        if (mainIcon) {

            const totalTiers =
                tiers.length;


            let highestCompletedTier = 0;


            tiers.forEach(
                tier => {

                    if (
                        tier.classList.contains(
                            "completed"
                        )
                    ) {

                        const tierNumber =
                            Number(
                                tier.dataset.tier
                            );


                        if (
                            tierNumber >
                            highestCompletedTier
                        ) {

                            highestCompletedTier =
                                tierNumber;

                        }

                    }

                }
            );


            mainIcon.src =
                getTierImage(
                    highestCompletedTier,
                    totalTiers
                );

            mainIcon.alt =
                `${highestCompletedTier}/${totalTiers}`;

        }


        /*
         * ------------------------------------------
         * UPDATE WHOLE ACHIEVEMENT
         * ------------------------------------------
         */

        const allTiersCompleted =
            tiers.length > 0 &&
            Array.from(tiers).every(
                tier =>
                    tier.classList.contains(
                        "completed"
                    )
            );


        item.classList.toggle(
            "completed",
            allTiersCompleted
        );

    }


    function updateOverallAchievementProgress() {

        if (!achievementData) {
            return;
        }


        const countElement =
            document.getElementById(
                "achievement-overall-count"
            );


        const percentElement =
            document.getElementById(
                "achievement-overall-percent"
            );


        const progressFill =
            document.getElementById(
                "achievement-overall-progress-fill"
            );


        if (
            !countElement ||
            !percentElement ||
            !progressFill
        ) {
            return;
        }


        let totalAchievements = 0;
        let completedAchievements = 0;


        /*
         * Every tier counts as its own achievement.
         *
         * Example:
         *
         * Achievement A
         *   Tier 1
         *   Tier 2
         *   Tier 3
         *
         * = 3 total achievements
         */

        achievementData.achievements.forEach(
            achievement => {

                if (
                    !Array.isArray(
                        achievement.tiers
                    )
                ) {
                    return;
                }


                achievement.tiers.forEach(
                    tier => {

                        totalAchievements++;


                        if (
                            tier.completed === true
                        ) {

                            completedAchievements++;

                        }

                    }
                );

            }
        );


        /*
         * No achievements available.
         */

        if (totalAchievements === 0) {

            countElement.textContent =
                "0 / 0";

            percentElement.textContent =
                "0%";

            progressFill.style.width =
                "0%";

            return;

        }


        /*
         * Calculate percentage.
         */

        const percentage =
            (
                completedAchievements /
                totalAchievements
            ) * 100;


        /*
         * Update the number.
         */

        countElement.textContent =
            `${completedAchievements} / ${totalAchievements}`;


        /*
         * Update percentage.
         */

        percentElement.textContent =
            `${percentage.toFixed(1)}%`;


        /*
         * Update progress bar.

         */

        progressFill.style.width =
            `${percentage}%`;

    }


    function updateTierAvailability(item) {

        const tiers =
            item.querySelectorAll(
                ".achievement-tier"
            );

        const mainIcon =
            item.querySelector(
                ".achievement-item-main-icon"
            );


        let previousCompleted = true;


        tiers.forEach(
            tier => {

                const button =
                    tier.querySelector(
                        ".achievement-complete-button"
                    );


                /*
                 * Lock tiers whose previous tier
                 * has not been completed.
                 */

                if (previousCompleted) {

                    tier.classList.remove(
                        "locked"
                    );

                    button.disabled = false;

                } else {

                    tier.classList.remove(
                        "completed"
                    );

                    button.classList.remove(
                        "completed"
                    );

                    button.title =
                        "Mark Completed";

                    tier.classList.add(
                        "locked"
                    );

                    button.disabled = true;

                }


                /*
                 * The next tier is only available
                 * when this tier is completed.
                 */

                previousCompleted =
                    !tier.classList.contains(
                        "locked"
                    ) &&
                    tier.classList.contains(
                        "completed"
                    );

            }
        );


        /*
         * Find the highest completed tier
         * after locked tiers have been removed.
         */

        let highestCompletedTier = 0;


        tiers.forEach(
            tier => {

                if (
                    tier.classList.contains(
                        "completed"
                    )
                ) {

                    const tierNumber =
                        Number(
                            tier.dataset.tier
                        );


                    if (
                        tierNumber >
                        highestCompletedTier
                    ) {

                        highestCompletedTier =
                            tierNumber;

                    }

                }

            }
        );


        /*
         * Update the large achievement icon.
         */

        if (mainIcon) {

            const totalTiers =
                tiers.length;


            mainIcon.src =
                getTierImage(
                    highestCompletedTier,
                    totalTiers
                );


            mainIcon.alt =
                `${highestCompletedTier}/${totalTiers}`;

        }

        /*
         * Update the entire achievement
         * when every tier is completed.
         */

        const allTiersCompleted =
            tiers.length > 0 &&
            Array.from(tiers).every(
                tier =>
                    tier.classList.contains(
                        "completed"
                    )
            );


                if (allTiersCompleted) {

                    item.classList.add(
                        "completed"
                    );

                } else {

                    item.classList.remove(
                        "completed"
                    );

                }

                updateAchievementProgress(item);

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