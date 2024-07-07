#include <stdio.h>
#include <string.h>

// Function declarations
void scanProduct();
void writeProductIDToFile(const char *productID);
void outputProductID(const char *productID);

int main() {
    scanProduct();
    return 0;
}

// Simulate scanning a product and write the product ID to a file
void scanProduct() {
    // Simulated product ID for demonstration purposes
    char productID[100] = "12345";

    // Print the simulated scanned product ID
    printf("Scanned Product ID: %s\n", productID);

    // Write the product ID to a file
    writeProductIDToFile(productID);

    // Output the product ID
    outputProductID(productID);
}

// Write the product ID to a file
void writeProductIDToFile(const char *productID) {
    FILE *file = fopen("product_id.txt", "w");
    if (file == NULL) {
        printf("Error opening file!\n");
        return;
    }
    fprintf(file, "%s", productID);
    fclose(file);
}

// Output the product ID
void outputProductID(const char *productID) {
    printf("Product ID has been written to file: %s\n", productID);
}
