/**process : get recipe data from html to   */
const BASE_URL = "http://127.0.0.1:5000"

async function processRecipe(evt) {
    let index = $(this).data("index")

    let label = $(`#recipe_label_${index}`)[0].innerText
    let image = $(`#recipe_image_${index}`)[0].currentSrc
    let cuisinetype = $(`#recipe_cuisinetype_${index}`)[0].innerText
    let dishtype = $(`#recipe_dishtype_${index}`)[0].innerText
    let mealtype = $(`#recipe_mealtype_${index}`)[0].innerText
    let ingredient = $(`#recipe_ingeredients_${index}`)[0].innerText

    const json = JSON.stringify({
        label: label,
        image: image,
        cuisinetype: cuisinetype,
        dishtype: dishtype,
        mealtype: mealtype,
        ingredient: ingredient
    })
    console.log(json)

    const res = await axios.post(`${BASE_URL}/api/add-recipe`, json, {
        headers: {
            'Content-Type': 'application/json'
        }
    })
    console.log(res.data)
}


$('button[id^="add_recipe_"]').on('click', processRecipe);

