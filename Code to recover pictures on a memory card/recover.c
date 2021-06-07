#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <cs50.h>
#define BLOCKSIZE 512

bool jpgheader(uint8_t buffer[])
{
    return (buffer[0] == 0xff && buffer[1] == 0xd8  && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0);
}

//Checking if the input is correct
int main(int argc, char *argv[])
{
    FILE *inputfile = fopen(argv[1], "r");
    if (argc != 2 && inputfile == NULL)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

//declaring variables needed

    uint8_t buffer[BLOCKSIZE];
    size_t fullbytes;
    bool firstjpeg = false;
    FILE *curr_file;
    char file_name[8];
    int counterjpeg = 0;
    bool jpegfound = false;

// Opening the memory card

    while (true)
//Reading into the card

    {
        fullbytes = fread(buffer, sizeof(uint8_t), BLOCKSIZE, inputfile);

        if (fullbytes == 0)
        {
            break;
        }

// New Jpeg discovered
        if (jpgheader(buffer))
        {
            jpegfound = true;

//Marking first JPEG
            if (!firstjpeg)
            {
                firstjpeg = true;
            }
            else
            {
                fclose(curr_file);

            }
            sprintf(file_name, "%03i.jpg", counterjpeg);
            curr_file = fopen(file_name, "w");
            fwrite(buffer, sizeof(uint8_t), fullbytes, curr_file);
            counterjpeg++;
        }
        else
//Write to file
        {
            if (jpegfound)
            {
                fwrite(buffer, sizeof(uint8_t), fullbytes, curr_file);
            }
        }
    }
//Closing all files
    fclose(inputfile);
    fclose(curr_file);
    return 0;
}



