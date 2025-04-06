// Common JavaScript functionality for the entire application

// Helper function to format numbers with commas
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Helper function to format dates
function formatDate(dateString) {
  const options = { year: "numeric", month: "long", day: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

// Helper function to show notifications
function showNotification(message, type = "info") {
  // Check if notification container exists, if not create it
  let notificationContainer = document.querySelector(".notification-container");

  if (!notificationContainer) {
    notificationContainer = document.createElement("div");
    notificationContainer.className = "notification-container";
    document.body.appendChild(notificationContainer);
  }

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
        <div class="notification-content">
            <p>${message}</p>
        </div>
        <button class="notification-close">&times;</button>
    `;

  // Add to container
  notificationContainer.appendChild(notification);

  // Add event listener to close button
  notification
    .querySelector(".notification-close")
    .addEventListener("click", () => {
      notification.classList.add("notification-hiding");
      setTimeout(() => {
        notification.remove();
      }, 300);
    });

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.classList.add("notification-hiding");
      setTimeout(() => {
        notification.remove();
      }, 300);
    }
  }, 5000);
}

// Add notification styles
const notificationStyles = document.createElement("style");
notificationStyles.textContent = `
    .notification-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 300px;
    }
    
    .notification {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        animation: notification-slide-in 0.3s ease;
    }
    
    .notification-hiding {
        animation: notification-slide-out 0.3s ease forwards;
    }
    
    .notification-info {
        border-left: 4px solid #4a6cf7;
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
    }
    
    .notification-warning {
        border-left: 4px solid #ffc107;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
    }
    
    .notification-content {
        flex: 1;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #6c757d;
    }
    
    @keyframes notification-slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes notification-slide-out {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;

document.head.appendChild(notificationStyles);

// Add placeholder image for recipe cards
document.addEventListener("DOMContentLoaded", () => {
  // Create a placeholder SVG for recipe images
  const createPlaceholderSVG = () => {
    return `
            <svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="300" height="200" fill="#f8f9fa"/>
                <text x="150" y="100" font-family="Arial" font-size="14" text-anchor="middle" fill="#6c757d">Recipe Image</text>
            </svg>
        `;
  };

  // Convert SVG to data URL
  const svgToDataURL = (svg) => {
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  };

  // Create recipe placeholder image directory
  const placeholderDir = "static/img";
  const placeholderPath = `${placeholderDir}/recipe-placeholder.jpg`;

  // Check if placeholder images exist, if not create them
  // Note: In a real app, you'd handle this server-side
  // This is just a client-side simulation
  const placeholderSVG = createPlaceholderSVG();
  const placeholderDataURL = svgToDataURL(placeholderSVG);

  // Set placeholder for recipe images that fail to load
  const recipeImages = document.querySelectorAll(".recipe-image img");
  recipeImages.forEach((img) => {
    img.onerror = function () {
      this.src = placeholderDataURL;
    };
  });
});

// Main JavaScript file for client-side functionality

// Handle recipe search form submission
document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.querySelector(".search-form");
  if (searchForm) {
    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const searchParams = new URLSearchParams(formData);
      window.location.href = `/search?${searchParams.toString()}`;
    });
  }

  // Handle servings adjustment
  const servingsInput = document.getElementById("servings");
  if (servingsInput) {
    servingsInput.addEventListener("change", function () {
      const servings = this.value;
      if (servings > 0) {
        adjustServings(servings);
      }
    });
  }

  // Handle recipe card hover effects
  const recipeCards = document.querySelectorAll(".recipe-card");
  recipeCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px)";
    });
    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });
});

// Function to adjust recipe servings
function adjustServings(servings) {
  const recipeId = document.querySelector('meta[name="recipe-id"]')?.content;
  if (!recipeId) return;

  fetch("/adjust_recipe", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      recipe_id: recipeId,
      servings: parseFloat(servings),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }
      updateIngredients(data.ingredients);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to adjust recipe");
    });
}

// Function to update ingredients list
function updateIngredients(ingredients) {
  const list = document.querySelector(".ingredients-list");
  if (!list) return;

  list.innerHTML = ingredients
    .map(
      (ing) => `
        <li>
            ${ing.amount ? `<span class="amount">${ing.amount}</span>` : ""}
            ${ing.unit ? `<span class="unit">${ing.unit}</span>` : ""}
            <span class="ingredient-name">${ing.name}</span>
        </li>
    `
    )
    .join("");
}

// Function to find recipes by ingredients
function findRecipesByIngredients(ingredients) {
  fetch("/find_by_ingredients", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ ingredients }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }
      displayMatchingRecipes(data);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to find recipes");
    });
}

// Function to display matching recipes
function displayMatchingRecipes(recipes) {
  const container = document.querySelector(".recipe-grid");
  if (!container) return;

  if (recipes.length === 0) {
    container.innerHTML = `
            <div class="no-results">
                <h2>No recipes found</h2>
                <p>Try adjusting your ingredients or browse all recipes.</p>
                <a href="/" class="btn">Browse All Recipes</a>
            </div>
        `;
    return;
  }

  container.innerHTML = recipes
    .map(
      (recipe) => `
        <div class="recipe-card">
            ${
              recipe.image_path
                ? `<img src="${recipe.image_path}" alt="${recipe.name}">`
                : `<img src="/static/images/placeholder.jpg" alt="${recipe.name}">`
            }
            <div class="recipe-info">
                <h3>${recipe.name}</h3>
                <p class="match-percentage">${
                  recipe.match_percentage
                }% match</p>
                <div class="matching-ingredients">
                    <h4>Matching Ingredients:</h4>
                    <ul>
                        ${recipe.matching_ingredients
                          .map((ing) => `<li>${ing}</li>`)
                          .join("")}
                    </ul>
                </div>
                <div class="missing-ingredients">
                    <h4>Missing Ingredients:</h4>
                    <ul>
                        ${recipe.missing_ingredients
                          .map((ing) => `<li>${ing}</li>`)
                          .join("")}
                    </ul>
                </div>
                <a href="/recipe/${
                  recipe.id
                }" class="view-recipe">View Recipe</a>
            </div>
        </div>
    `
    )
    .join("");
}

// Function to handle image upload for measurement
function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("image", file);

  fetch("/measure", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }
      displayMeasurementResult(data);
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to process image");
    });
}

// Function to display measurement result
function displayMeasurementResult(data) {
  const resultContainer = document.querySelector(".measurement-result");
  if (!resultContainer) return;

  resultContainer.innerHTML = `
        <h3>Measurement Result</h3>
        <p>Detected amount: ${data.amount} ${data.unit}</p>
        <p>Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
        <div class="conversions">
            <h4>Common Conversions:</h4>
            <ul>
                ${data.conversions
                  .map(
                    (conv) => `
                    <li>${conv.amount} ${conv.unit}</li>
                `
                  )
                  .join("")}
            </ul>
        </div>
    `;
}
