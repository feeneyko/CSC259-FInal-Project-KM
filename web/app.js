const pigments = [
    'White', 'Black', 'Cobalt Blue', 'Quinacridone Magenta',
    'Phthalo Blue (Green Shade)', 'Hansa Yellow', 'Phthalo Green',
    'Pyrrole Red', 'Ultramarine Blue', 'Dioxazine Purple', 'Pyrrole Orange'
];

let pigmentData = [];

// Load JSON data file
async function loadData() {
    pigmentData = await fetch('prepared_data.json').then(res => res.json());
    displayPigments();
}
// Display each pigment as a selectable color swatch
function displayPigments() {
    const container = document.getElementById('pigment-container');
    pigments.forEach(pigment => {
        const colorBox = document.createElement('div');
        colorBox.classList.add('pigment-box');
        colorBox.style.width = '100px';
        colorBox.style.height = '100px';
        colorBox.style.display = 'inline-block';
        colorBox.style.margin = '5px';
        colorBox.style.border = '1px solid #000';
        colorBox.style.cursor = 'pointer';
        colorBox.style.position = 'relative';
        colorBox.dataset.pigment = pigment;

        // Calculate and display the pigment color initially
        const rgb = calculateColor(pigment);
        colorBox.style.backgroundColor = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;

        const label = document.createElement('div');
        label.textContent = pigment;
        label.style.position = 'absolute';
        label.style.bottom = '0';
        label.style.width = '100%';
        label.style.textAlign = 'center';
        label.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';

        colorBox.appendChild(label);
        colorBox.addEventListener('click', () => togglePigmentSelection(colorBox));
        container.appendChild(colorBox);
    });
}

// Toggle selection state for a pigment and manage individual ratio input fields
function togglePigmentSelection(element) {
    element.classList.toggle('selected');

    if (element.classList.contains('selected')) {
        element.style.border = '3px solid #ff0000';
    } else {
        element.style.border = '1px solid #000';
    }

    // Get all selected pigments and clear the container
    const selectedElements = document.querySelectorAll('.pigment-box.selected');
    const selectedPigmentsContainer = document.getElementById('selected-pigments');
    selectedPigmentsContainer.innerHTML = '<h3>Selected Pigments and Ratios</h3>';

    // Iterate through all selected pigments and recreate the ratio fields in the correct order
    selectedElements.forEach(selectedElement => {
        const selectedPigmentName = selectedElement.dataset.pigment;
        const ratioField = document.createElement('div');
        ratioField.id = `ratio-${selectedPigmentName}`;
        ratioField.innerHTML = `
            <label>${selectedPigmentName} Ratio:</label>
            <input type="number" class="pigment-ratio" data-pigment="${selectedPigmentName}" min="0" value="1" style="width: 50px; margin-left: 5px; margin-top: 4px;" placeholder="0">
        `;
        selectedPigmentsContainer.appendChild(ratioField);
    });

    if (selectedElements.length > 2) {
        const dotsizeContainer = document.getElementById('dotsize-input-div');
        dotsizeContainer.innerHTML = 
        `
            <label for="dotsize-input">Enter Dot Size:</label>
            <input type="number" id="dotsize-input" value="8">
        `;
    }
}

function calculateColor(pigments, ratios = [1]) {
    // Mapping of pigment names to column names in the pigment data
    const pigment_mapping = {
        'White': 'white',
        'Black': 'black',
        'Cobalt Blue': 'cobalt b',
        'Quinacridone Magenta': 'quinacridone Magenta',
        'Phthalo Blue (Green Shade)': 'phthalo blue (green shade)',
        'Hansa Yellow': 'hansa Yellow',
        'Phthalo Green': 'phthalo Green',
        'Pyrrole Red': 'pyrrole Red',
        'Ultramarine Blue': 'ultramarine Blue',
        'Dioxazine Purple': 'dioxazine Purple',
        'Pyrrole Orange': 'pyrrole Orange'
    };
    // Check if pigments is a single string (single pigment) or an array (multiple pigments)
    if (typeof pigments === 'string') {
        pigments = [pigments]; // Convert to array for uniform processing
    }

    // Initialize variables to hold the weighted sum of K and S values
    let weightedK = Array(pigmentData.length).fill(0);
    let weightedS = Array(pigmentData.length).fill(0);
    let totalRatio = ratios.reduce((sum, r) => sum + r, 0);

    // Loop through each pigment and add its weighted K and S values
    pigments.forEach((pigmentName, index) => {
        const pigmentKey = pigment_mapping[pigmentName];
        const k_col = `k ${pigmentKey}`;
        const s_col = `s ${pigmentKey}`;
        
        // Retrieve K and S values for the current pigment
        const K = pigmentData.map(row => row[k_col]);
        const S = pigmentData.map(row => row[s_col]);
        const ratio = ratios[index] / totalRatio;  // Normalize the ratio

        // Add the weighted K and S values to the total
        K.forEach((k, i) => {
            weightedK[i] += k * ratio;
            weightedS[i] += S[i] * ratio;
        });
    });

    // Calculate R_inf based on the weighted K and S values
    const ks_ratio = weightedK.map((k, i) => k / weightedS[i]);
    const R_inf = ks_ratio.map(ks => 1 + ks - Math.sqrt(ks * (ks + 2))).map(r => Math.min(Math.max(r, 0), 1));

    // Extract color matching functions and illuminant data from the pigmentData
    const x_bar = pigmentData.map(row => row.x_bar);
    const y_bar = pigmentData.map(row => row.y_bar);
    const z_bar = pigmentData.map(row => row.z_bar);
    const I = pigmentData.map(row => row.power);
    const delta_lambda = pigmentData[1].wavelength - pigmentData[0].wavelength;

    // Calculate XYZ tristimulus values
    const X_num = R_inf.reduce((acc, R, i) => acc + R * I[i] * x_bar[i], 0) * delta_lambda;
    const Y_num = R_inf.reduce((acc, R, i) => acc + R * I[i] * y_bar[i], 0) * delta_lambda;
    const Z_num = R_inf.reduce((acc, R, i) => acc + R * I[i] * z_bar[i], 0) * delta_lambda;
    const Y_norm = I.reduce((acc, I, i) => acc + I * y_bar[i], 0) * delta_lambda;

    const X = X_num / Y_norm;
    const Y = Y_num / Y_norm;
    const Z = Z_num / Y_norm;

    return xyz_to_rgb(X, Y, Z);
}

function gammaCorrect(c) {
    if (c <= 0) {
        return 0;
    } else if (c <= 0.0031308) {
        return 12.92 * c;
    } else if (c < 1) {
        return 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
    } else {
        return 1;
    }
}

function inverseGammaCorrect(c) {
    return Math.pow(c, 2.2);
}

// Mix colors based on selected pigments and given ratios
function mixColors() {
    const selectedElements = document.querySelectorAll('.pigment-box.selected');
    const selectedPigments = Array.from(selectedElements).map(el => el.dataset.pigment);
    
    if (selectedPigments.length < 2) {
        alert("Please select (click) at least two pigments to mix.");
        return;
    }

    const ratioFields = document.querySelectorAll('.pigment-ratio');
    const ratios = Array.from(ratioFields).map(input => Number(input.value));

    console.log(selectedPigments, ratios);

    let mixedRGB = [0, 0, 0];
    let totalRatio = ratios.reduce((sum, r) => sum + r, 0);

    // RGB Light Mixing
    selectedPigments.forEach((pigment, index) => {
        const rgb = calculateColor(pigment).map(c => c / 255).map(inverseGammaCorrect);
        mixedRGB[0] += rgb[0] * (ratios[index] / totalRatio);
        mixedRGB[1] += rgb[1] * (ratios[index] / totalRatio);
        mixedRGB[2] += rgb[2] * (ratios[index] / totalRatio);
    });
    mixedRGB = mixedRGB.map(gammaCorrect).map(c => Math.round(c * 255));
    displayMixedColor(mixedRGB);
    
    displayMixedColorKM(calculateColor(selectedPigments, ratios));
}

function calculateGamut() {
    const stepsInput = document.getElementById('fraction-input');
    const dotsizeInput = document.getElementById('dotsize-input');

    const selectedElements = document.querySelectorAll('.pigment-box.selected');
    const selectedPigments = Array.from(selectedElements).map(el => el.dataset.pigment);
    
    if (selectedPigments.length < 2) {
        alert("Please select at least two pigments to calculate the gamut.");
        return;
    } else if (selectedPigments.length == 2) {
        let steps = parseInt(stepsInput.value);
        const combinations = generateRatioCombinations(selectedPigments.length, steps);

        // For each combination, calculate the color
        const colors = combinations.map(ratios => {
            const rgb = calculateColor(selectedPigments, ratios);
            return {
                rgb: rgb,
                ratios: ratios
            };
        });
        displayGamut(colors, selectedPigments, steps);
    } else if (selectedPigments.length == 3) {
        let steps = parseInt(stepsInput.value);
        let dotsize = parseInt(dotsizeInput.value);
        // Generate combinations of ratios for three pigments
        const combinations = generateRatioCombinations(3, steps);

        // For each combination, calculate the color
        const colors = combinations.map(ratios => {
            const rgb = calculateColor(selectedPigments, ratios);
            return {
                rgb: rgb,
                ratios: ratios
            };
        });
        // Display the gamut using a ternary plot
        displayGamut(colors, selectedPigments, dotsize);
    } else {
        alert("Please select at most three pigments to calculate the gamut.");
        return;
    }
}

// Function to generate all combinations of ratios that sum to 1
function generateRatioCombinations(n, steps) {
    const combinations = [];

    if (n == 2) {
        // Existing code for two pigments
        for (let i = 0; i <= steps; i++) {
            const ratio1 = i / steps;
            const ratio2 = (steps - i) / steps;
            combinations.push([ratio1, ratio2]);
        }
    } else if (n == 3) {
        // Generate combinations for three pigments
        for (let i = 0; i <= steps; i++) {
            for (let j = 0; j <= steps - i; j++) {
                const k = steps - i - j;
                const ratio1 = i / steps;
                const ratio2 = j / steps;
                const ratio3 = k / steps;
                combinations.push([ratio1, ratio2, ratio3]);
            }
        }
    } else {
        // For n != 2 or 3, return an empty array
        return [];
    }

    return combinations;
}

// Function to display the gamut of colors for three pigments using a ternary plot
function displayGamut(colors, selectedPigments, dotsize) {
    const gamutContainer = document.getElementById('gamut-container');
    gamutContainer.innerHTML = ''; // Clear previous content

    if (selectedPigments.length == 2) {
        // Existing code for two pigments
        colors.forEach(colorObj => {
            const colorDiv = document.createElement('div');
            colorDiv.style.width = '40px';
            colorDiv.style.height = '40px';
            colorDiv.style.display = 'inline-block';
            colorDiv.style.margin = '1px';
            const [r, g, b] = colorObj.rgb;
            colorDiv.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
            
            const ratioDiv = document.createElement('div');
            ratioDiv.style.fontSize = '16px';
            ratioDiv.style.textAlign = 'center';
            ratioDiv.innerHTML = colorObj.ratios.map(r => `<div>${r.toFixed(2)}</div>`).join('');

            const containerDiv = document.createElement('div');
            containerDiv.style.display = 'inline-block';
            containerDiv.style.margin = '5px';
            containerDiv.appendChild(colorDiv);
            containerDiv.appendChild(ratioDiv);

            gamutContainer.appendChild(containerDiv);
        });
    } else if (selectedPigments.length == 3) {
        // Create a canvas for the ternary plot
        const canvas = document.createElement('canvas');
        const canvasWidth = 500;
        const canvasHeight = Math.floor(canvasWidth * Math.sqrt(3) / 2);
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;
        const ctx = canvas.getContext('2d');

        // Draw the ternary plot background (triangle)
        drawTernaryBackground(ctx, canvasWidth, canvasHeight, selectedPigments);

        // Plot each color point on the ternary plot
        colors.forEach(colorObj => {
            const [r, g, b] = colorObj.rgb;
            const ratios = colorObj.ratios;

            // Convert ternary ratios to Cartesian coordinates
            const [x, y] = ternaryToCartesian(ratios, canvasWidth, canvasHeight);

            // TODO: Color point size based on ratio
            // TODO: make the color point clickable to display the ratios
            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.beginPath();
            // ctx.arc(x, y, 2, 0, 2 * Math.PI); // Use y directly
            ctx.arc(x, canvasHeight - y, dotsize, 0, 2 * Math.PI); // Invert y-axis
            ctx.fill();
        });

        gamutContainer.appendChild(canvas);
    }
}

// Function to convert ternary ratios to Cartesian coordinates
// function ternaryToCartesian(ratios, canvasWidth, canvasHeight) {
//     const [a, b, c] = ratios;

//     // Calculate x coordinate
//     const x = a * 0 + b * canvasWidth + c * (canvasWidth / 2);

//     // Calculate y coordinate (inverted to match canvas coordinates)
//     const y = canvasHeight - c * canvasHeight;

//     return [x, y];
// }

function ternaryToCartesian(ratios, canvasWidth, canvasHeight, padding = 34) {
    const [a, b, c] = ratios;
    const sum = a + b + c || 1; // Prevent division by zero
    const x = (0.5 * (2 * b + c)) / sum;
    const y = (Math.sqrt(3) / 2) * c / sum;

    // Scale to canvas size with padding
    const effectiveWidth = canvasWidth - 2 * padding;
    const effectiveHeight = canvasHeight - 2 * padding;

    const scaledX = padding + x * effectiveWidth;
    const scaledY = padding + y * effectiveHeight / (Math.sqrt(3) / 2);

    return [scaledX, scaledY];
}

// Function to draw the ternary plot background and labels
function drawTernaryBackground(ctx, canvasWidth, canvasHeight, pigmentNames) {
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1;

    // Label positions
    const fontSize = 14;
    ctx.font = `${fontSize}px Arial`;
    ctx.fillStyle = '#000';

    // Left corner (Pigment A)
    const colorA = calculateColor(pigmentNames[0]);
    ctx.fillStyle = `rgb(${colorA[0]}, ${colorA[1]}, ${colorA[2]})`;
    ctx.fillText(pigmentNames[0], 0, canvasHeight);

    // Right corner (Pigment B)
    const colorB = calculateColor(pigmentNames[1]);
    ctx.fillStyle = `rgb(${colorB[0]}, ${colorB[1]}, ${colorB[2]})`;
    const textWidthB = ctx.measureText(pigmentNames[1]).width;
    ctx.fillText(pigmentNames[1], canvasWidth - textWidthB, canvasHeight);

    // Top corner (Pigment C)
    const colorC = calculateColor(pigmentNames[2]);
    ctx.fillStyle = `rgb(${colorC[0]}, ${colorC[1]}, ${colorC[2]})`;
    const textWidthC = ctx.measureText(pigmentNames[2]).width;
    ctx.fillText(pigmentNames[2], (canvasWidth / 2) - (textWidthC / 2), fontSize);
}

// Display the mixed color
function displayMixedColor(rgb) {
    const colorDisplayRGB = document.getElementById('RGB-mixed-color-display');
    colorDisplayRGB.style.backgroundColor = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
    const colorInfoRGB = document.getElementById('RGB-mixed-color-info');
    colorInfoRGB.textContent = `Mixed sRGB values: ${rgb[0]}, ${rgb[1]}, ${rgb[2]}`;
}

function displayMixedColorKM(rgb) {
    const colorDisplayKM = document.getElementById('KM-mixed-color-display');
    colorDisplayKM.style.backgroundColor = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
    const colorInfoKM = document.getElementById('KM-mixed-color-info');
    colorInfoKM.textContent = `Mixed sRGB values: ${rgb[0]}, ${rgb[1]}, ${rgb[2]}`;
}

// Convert XYZ values to sRGB
function xyz_to_rgb(X, Y, Z) {
    const M = [
        [3.2406, -1.5372, -0.4986],
        [-0.9689, 1.8758, 0.0415],
        [0.0557, -0.2040, 1.0570]
    ];

    let [r, g, b] = [0, 1, 2].map(i => M[i][0] * X + M[i][1] * Y + M[i][2] * Z);
    [r, g, b] = [r, g, b].map(c => Math.max(0, Math.min(1, c)));

    return [r, g, b].map(gammaCorrect).map(c => Math.round(c * 255));
}

// Load all data on startup
loadData();
