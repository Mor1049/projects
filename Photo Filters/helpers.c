#include "helpers.h"
#include <math.h>
#include <memory.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int p = 0; p < height; p++)
    {
        for (int j = 0; j < width; j++)
        {
//Getting colour values
            int red = image[p][j].rgbtRed;
            int blue = image[p][j].rgbtBlue;
            int green = image[p][j].rgbtGreen;
//Finding the average
            float avg = round((red + blue + green) / 3.0);

            image[p][j].rgbtRed = avg;
            image[p][j].rgbtBlue = avg;
            image[p][j].rgbtGreen = avg;
        }
    }
    return;
}
//Function initialization so we have a limit of 255
int max(int limit)

{
    return limit > 255 ? 255 : limit;
}


// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int p = 0; p < height; p++)
    {
        for (int j = 0; j < width; j++)
        {
            int red = image[p][j].rgbtRed;
            int green = image[p][j].rgbtGreen;
            int blue = image[p][j].rgbtBlue;

            image[p][j].rgbtRed = max(round(0.393 * red + 0.769 * green + 0.189 * blue));
            image[p][j].rgbtGreen = max(round(0.349 * red + 0.686 * green + 0.168 * blue));
            image[p][j].rgbtBlue = max(round(0.272 * red + 0.534 * green + 0.131 * blue));

        }
    }
}


// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
//Initialization of array to swap values
    int temporary[3];

    for (int p = 0; p < height; p++)
    {
//Iterate through the picture and fill the array
        for (int k = 0; k < (width / 2); k++)
        {
            temporary[0] = image[p][k].rgbtRed;
            temporary[1] = image[p][k].rgbtBlue;
            temporary[2] = image[p][k].rgbtGreen;

//Exchange the pixels
            image[p][k].rgbtRed = image[p][width - k - 1].rgbtRed;
            image[p][k].rgbtBlue = image[p][width - k - 1].rgbtBlue;
            image[p][k].rgbtGreen = image[p][width - k - 1].rgbtGreen;

            image[p][width - k - 1].rgbtRed = temporary[0];
            image[p][width - k - 1].rgbtBlue = temporary[1];
            image[p][width - k - 1].rgbtGreen = temporary[2];


        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temporary[height][width];

    for (int xaxis = 0; xaxis < height; xaxis++)
    {
//Initialization of values
        for (int yaxis = 0; yaxis < width; yaxis++)
        {
            int curxaxis[] = { xaxis - 1, xaxis, xaxis + 1 };
            int curyaxis[] = { yaxis - 1, yaxis, yaxis + 1 };
            float finalred = 0;
            float finalgreen = 0;
            float finalblue = 0;
            int counter = 0;
//Iteration through the pixels
            for (int m = 0; m < 3; m++)
            {
                for (int n = 0; n < 3; n++)
                {
                    int row = curxaxis[m];
                    int column = curyaxis[n];


                    if (column < width && column >= 0 && row < height && row >= 0)
                    {
                        RGBTRIPLE pixel = image[row][column];
//Add the values up
                        finalred = pixel.rgbtRed + finalred;
                        finalgreen = pixel.rgbtGreen + finalgreen;
                        finalblue = pixel.rgbtBlue + finalblue;
                        counter++;
                    }

                }
            }
//Check neighbour cells
            temporary[xaxis][yaxis].rgbtRed = round(finalred / counter);
            temporary[xaxis][yaxis].rgbtGreen = round(finalgreen / counter);
            temporary[xaxis][yaxis].rgbtBlue = round(finalblue / counter);
        }
    }
//Copyint to final image
    for (int m = 0; m < height; m++)
    {
        for (int n = 0; n < width; n++)
        {
            image[m][n] = temporary[m][n] ;
        }
    }
}
