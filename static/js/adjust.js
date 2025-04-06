document.addEventListener("DOMContentLoaded", function () {
  // Get all recipe cards
  const recipeCards = document.querySelectorAll(".recipe-card");
  const adjustmentForm = document.querySelector(".adjustment-form");
  const servingsInput = document.getElementById("servings");
  const textureSelect = document.getElementById("texture");
  const ingredientsList = document.getElementById("ingredients-list");
  const originalServings = parseInt(
    document.getElementById("original-servings").value
  );
  const originalIngredients = JSON.parse(
    document.getElementById("original-ingredients").value
  );

  // Add click event to recipe cards
  recipeCards.forEach((card) => {
    card.addEventListener("click", function () {
      // Remove selected class from all cards
      recipeCards.forEach((c) => c.classList.remove("selected"));
      // Add selected class to clicked card
      this.classList.add("selected");
      // Show adjustment form
      adjustmentForm.style.display = "block";
      // Update recipe name in form
      document.querySelector(".adjustment-form h2 span").textContent =
        this.querySelector("h3").textContent;
    });
  });

  // Handle servings change
  servingsInput.addEventListener("change", function () {
    const newServings = parseInt(this.value);
    const ratio = newServings / originalServings;

    // Update ingredients list
    ingredientsList.innerHTML = "";
    originalIngredients.forEach((ingredient) => {
      const newAmount = (ingredient.amount * ratio).toFixed(2);
      const li = document.createElement("li");
      li.innerHTML = `
                <div class="ingredient-item">
                    <div class="original-amount">
                        <span class="label">Original:</span>
                        <span class="amount">${ingredient.amount}</span>
                        <span class="unit">${ingredient.unit}</span>
                    </div>
                    <div class="adjusted-amount">
                        <span class="label">Adjusted:</span>
                        <span class="amount">${newAmount}</span>
                        <span class="unit">${ingredient.unit}</span>
                    </div>
                    <div class="ingredient-name">${ingredient.name}</div>
                </div>
            `;
      ingredientsList.appendChild(li);
    });
  });

  // Handle texture change
  textureSelect.addEventListener("change", function () {
    const texture = this.value;
    const tipsList = document.getElementById("tips-list");

    // Update tips based on texture
    tipsList.innerHTML = "";
    const tips = getTextureTips(texture);
    tips.forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = tip;
      tipsList.appendChild(li);
    });
  });

  // Function to get texture-specific tips
  function getTextureTips(texture) {
    const tips = {
      soft: [
        "Add 1-2 tablespoons more liquid",
        "Reduce baking time by 5 minutes",
        "Use room temperature ingredients",
      ],
      firm: [
        "Reduce liquid by 1-2 tablespoons",
        "Increase baking time by 5 minutes",
        "Use chilled ingredients",
      ],
      crunchy: [
        "Add 1/4 cup more sugar",
        "Increase baking time by 10 minutes",
        "Use cold butter",
      ],
    };
    return tips[texture] || [];
  }

  // Handle form submission
  document
    .querySelector(".adjustment-form form")
    .addEventListener("submit", function (e) {
      e.preventDefault();

      // Get form data
      const formData = {
        servings: servingsInput.value,
        texture: textureSelect.value,
        ingredients: Array.from(ingredientsList.children).map((li) => ({
          name: li.querySelector(".ingredient-name").textContent,
          amount: parseFloat(li.querySelector(".amount").textContent),
          unit: li.querySelector(".unit").textContent,
        })),
      };

      // Send data to server
      fetch("/api/adjust_recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Show success message
            alert("Recipe adjusted successfully!");
            // Reset form
            this.reset();
            // Hide form
            adjustmentForm.style.display = "none";
            // Remove selected class from recipe card
            document
              .querySelector(".recipe-card.selected")
              .classList.remove("selected");
            // Display adjustment results
            displayResults(data);
          } else {
            alert("Error adjusting recipe: " + data.message);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Error adjusting recipe. Please try again.");
        });
    });

  // Display adjustment results
  function displayResults(data) {
    // Set meta information
    resultsServings.textContent = `${data.adjusted_servings} Servings`;

    let textureLabel;
    switch (data.texture) {
      case "moist":
        textureLabel = "More Moist";
        break;
      case "crispy":
        textureLabel = "More Crispy";
        break;
      default:
        textureLabel = "Normal Texture";
    }
    resultsTexture.textContent = textureLabel;

    // Generate ingredients table
    ingredientsResults.innerHTML = "";
    data.adjusted_ingredients.forEach((ingredient) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                    <td><strong>${ingredient.name}</strong></td>
                    <td>${ingredient.original_amount}</td>
                    <td class="adjusted">${ingredient.adjusted_amount}</td>
                `;
      ingredientsResults.appendChild(row);
    });

    // Generate baking notes
    bakingNotes.innerHTML = "";
    const notes = [
      {
        condition: data.texture !== "normal",
        text: `This recipe has been adjusted for ${textureLabel.toLowerCase()} texture.`,
      },
      {
        condition: data.adjusted_servings > data.original_servings,
        text: `You may need to use a larger baking dish for this increased quantity.`,
      },
      {
        condition: data.adjusted_servings !== data.original_servings,
        text: `Baking time may need to be adjusted slightly. Check for doneness a few minutes earlier or later than the original recipe.`,
      },
    ];

    notes.forEach((note) => {
      if (note.condition) {
        const li = document.createElement("li");
        li.textContent = note.text;
        bakingNotes.appendChild(li);
      }
    });

    // Add a general note about precision
    const precisionNote = document.createElement("li");
    precisionNote.textContent =
      "For best results, use a kitchen scale for precise measurements.";
    bakingNotes.appendChild(precisionNote);

    // Show results container
    resultsContainer.style.display = "block";
    resultsContainer.scrollIntoView({ behavior: "smooth" });
  }
});
