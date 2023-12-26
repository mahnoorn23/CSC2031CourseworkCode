// JavaScript function to generate 6 random unique values in order and populate form
function luckyDip() {

    // Create empty set
    let draw = new Set();

    // While set does not contain 6 values, create a random value between 1 and 60
    while (draw.size < 6) {
        min = 1;
        max = 60;
        // Create an array of length 6
        randomBuffer = new Uint32Array(6);
        // Filling the array with cryptographically secure integers
        window.crypto.getRandomValues(randomBuffer)

        for (let i = 0; i < randomBuffer.length; i++) {

            csRandomNumber = randomBuffer[i] / (0xFFFFFFFF)
            value = Math.floor(csRandomNumber * (max - min + 1) + min);

            // Sets cannot contain duplicates so value is only added if it does not exist in set
            draw.add(value)
        }
    }

    // Turn set into an array
    let a = Array.from(draw);

    // Sort array into size order
    a.sort(function (a, b) {
        return a - b;
    });

    // Add values to fields in create draw form
    for (let i = 0; i < 6; i++) {
        document.getElementById("no" + (i + 1)).value = a[i];
    }
}