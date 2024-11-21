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
            <input type="number" class="pigment-ratio" data-pigment="${selectedPigmentName}" min="0" value="1" style="width: 50px; margin-left: 5px;">
        `;
        selectedPigmentsContainer.appendChild(ratioField);
    });
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
    return Math.pow(c, 1 / 2.2);
}

function inverseGammaCorrect(c) {
    return Math.pow(c, 2.2);
}


// Mix colors based on selected pigments and given ratios
function mixColors() {
    const selectedElements = document.querySelectorAll('.pigment-box.selected');
    const selectedPigments = Array.from(selectedElements).map(el => el.dataset.pigment);

    const ratioFields = document.querySelectorAll('.pigment-ratio');
    const ratios = Array.from(ratioFields).map(input => Number(input.value));

    if (selectedPigments.length !== ratios.length) {
        alert("Please ensure that all selected pigments have a ratio.");
        return;
    }

    let mixedRGB = [0, 0, 0];
    let totalRatio = ratios.reduce((sum, r) => sum + r, 0);

    selectedPigments.forEach((pigment, index) => {
        const rgb = calculateColor(pigment).map(c => c / 255).map(inverseGammaCorrect);
        mixedRGB[0] += rgb[0] * (ratios[index] / totalRatio);
        mixedRGB[1] += rgb[1] * (ratios[index] / totalRatio);
        mixedRGB[2] += rgb[2] * (ratios[index] / totalRatio);
    });

    mixedRGB = mixedRGB.map(gammaCorrect).map(c => Math.round(c * 255));

    displayMixedColor(mixedRGB.map(Math.round));
    displayMixedColorKM(calculateColor(selectedPigments, ratios));
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
