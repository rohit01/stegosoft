/*
 * stegno_decrypt_header.c
 *
 *  Created on: May 2, 2011
 *      Author: Rohit Gupta
 *
 *  Program to Unhide Message in a wav audio file.
 *
 *  License: GNU GPL v2
 *
 *  Header Format:
 *  1. Main Header (size 48 bits + variable):
 *  --------------------------------------------------
 *  |  Version  |  Header Len  |  Bit Gap (x8 bytes) |
 *  |  (4 bits) |  (24 bits)   |     ( 8 bits )      |
 *  --------------------------------------------------
 *  |   Encrypt All   |   No. of Message Files       |
 *  |    (4 bits)     |   (8 bits for 255 files)     |
 *  --------------------------------------------------
 *  | Password Size   |         Password             |
 *  |  (16 bits)      | (variable - password_size*8) |
 *  --------------------------------------------------
 *
 *  2. Optional Header (size 44 + variable )
 *  -------------------------------------------------
 *  |  File Size  |  Filename size  |  Encryption   |
 *  |  (32 bits)  |    ( 8 bits )   |   (4 bits)    |
 *  -------------------------------------------------
 *  |  File Name ( max 255 bytes, variable)         |
 *  -------------------------------------------------
 *
 *  Possible header size = 48 bits to 141845 bits
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>


typedef struct mhs{
/*
 * Structure to store 1 (one) message details
 * for header
 */
	unsigned long int file_size, filename_size, encryption;
	char *filename;
} message_header_structure;

unsigned long int extract_filename_index_from_full_path(char *file);
char extract_character_from_carrier_file( FILE *carrier_file, unsigned long int *cursor_postion,
		unsigned long int *cursor_loop_max, unsigned long int bit_gap );
unsigned long int extract_integer_from_carrier_file( FILE *carrier_file, unsigned long int *cursor_postion,
		unsigned long int *cursor_loop_max, unsigned long int no_of_bits, unsigned long int bit_gap );

int main(int no_of_arguments, char *cmd_line_arguments[] ){
/*
 * Information in Arguments:
 * 1. Carrier Filename (Full path or relative)
 * 2. Output Folder Full Path
 * 3. password
 *
 */
	char *carrier_filename, *output_folder_full_path, *output_message_full_path, *password, *password_carrier;
	unsigned long int carrier_filesize, no_of_message_files, encrypt_all, password_size, header_len, bit_gap, total_message_filesize, version=1, carrier_version;
	message_header_structure  *message_details;
	FILE *carrier_file, *output_message_file;

/*
 *  Temporary variable declarations:
 */
	unsigned char tmp_char1;
	unsigned long int i, j, tmp_int, cursor_position, cursor_loop_max, ms_bit, ms_mask, ls_mask;

/*
 * Initialize variables from command line arguments
 */
	carrier_filename = cmd_line_arguments[1];
	output_folder_full_path = cmd_line_arguments[2];
	password = cmd_line_arguments[3];

/*
 * Open the Carrier file
 */
	carrier_file = fopen( carrier_filename, "r" );

/*
 * Initialize the variables
 */
	cursor_position = 0;
	cursor_loop_max = 0;

/*
 * Skip the first 50 bytes for
 * wav format header
 */
	cursor_loop_max += 50;
	for(cursor_position=0; cursor_position < cursor_loop_max; cursor_position++){
		fgetc( carrier_file );
	}

/*
 * Verify the version (1)
 * no. of bits = 4
 * bit gap for all header info = 1
 */

	carrier_version = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 4, 1 );
	if( carrier_version != version ){
		fclose( carrier_file );
		return 1;
	}

/*
 * Inspect the Header information and initialize
 * the Header variables respectively
 */

/*
 * Header Length (24 bits)
 */
	header_len = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 24, 1);

/*
 * Bit Gap (8 bits)
 */
	bit_gap = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 8, 1);

/*
 * Encrypt All (4 bits)
 */
	encrypt_all = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 4, 1);

/*
 * No of message files (8 bits)
 */
	no_of_message_files = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 8, 1);

/*
 * Verify if password is stored
 * and extract if stored
 */
	if( encrypt_all != 0 ){
	/*
	 * extract password size (16 bits)
	 */
		password_size = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 16, 1);
	/*
	 * Allocate memory to password variable
	 * and extract password
	 */
		password_carrier = calloc( password_size + 1 , sizeof(char) );
		for(i=0; i < password_size; i++){
			password_carrier[i] = extract_character_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 1);
			printf("%c\n", password_carrier[i]);
		}
		password_carrier[i] = '\0';

		i = strcmp(password, password_carrier);
		if( i != 0 ){
			fclose( carrier_file );
			return 1;
		}
	}

/*
 * Allocate memory to store hidden message
 * details in "message_details" variable
 */
	message_details = calloc( no_of_message_files, sizeof(message_header_structure) );

/*
 * Extract Message details from header
 */
	for(i=0; i < no_of_message_files; i++){
		message_details[i].file_size = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 32, 1);
		message_details[i].filename_size = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 8, 1);
		message_details[i].encryption = extract_integer_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 4, 1);
	/*
	 * Allocate memory to store message filename
	 */
		message_details[i].filename = calloc( message_details[i].filename_size + 1, sizeof(char));
	/*
	 * Extract filename
	 */
		for(j=0; j < message_details[i].filename_size; j++){
			message_details[i].filename[j] = extract_character_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, 1);
		}
		message_details[i].filename[j] = '\0';
	}

/*
 * Extract the message files in the output folder
 * with respective message filename
 */
	for(i=0; i < no_of_message_files; i++){
	/*
	 * Allocate memory for output_message_full_path
	 * variable
	 */
		output_message_full_path = calloc( strlen(output_folder_full_path) +
				strlen( message_details[i].filename ) + 1, sizeof(char) );

	/*
	 * Initialize the variable
	 * output_message_full_path
	 */
		strcpy( output_message_full_path, output_folder_full_path );
		strcat( output_message_full_path, message_details[i].filename );
	/*
	 * open a message for writing
	 */
		output_message_file = fopen( output_message_full_path, "w" );

	/*
	 * Write the message file
	 */
		for(j=0; j < message_details[i].file_size; j++ ){
			tmp_char1 = extract_character_from_carrier_file( carrier_file, &cursor_position, &cursor_loop_max, bit_gap );
			fputc( tmp_char1, output_message_file );
		}
	/*
	 * close the file and free the used memory
	 */
		fclose( output_message_file );
		free( output_message_full_path );
		free( message_details[i].filename );
	}

/*
 * close the file and free the used memory
 */
	fclose( carrier_file );
	free( message_details );

	return 0;
}

unsigned long int extract_filename_index_from_full_path(char *file){
/*
 * Takes input a string (file full path name) and
 * returns the index of the starting character of
 * filename
 */
	int i, return_ans = 0;
	for(i=0; file[i] != '\0'; i++){
		if(file[i] == '/'){
			return_ans = i+1;
		}
	}
	return return_ans;
}


unsigned long int extract_integer_from_carrier_file( FILE *carrier_file, unsigned long int *cursor_postion,
		unsigned long int *cursor_loop_max, unsigned long int no_of_bits, unsigned long int bit_gap ){
/*
 * Variable declaration to store partial results
 */
	unsigned long int integer_stored;

/*
 * Temporary variable declarations
 */
	char tmp_char1;
	unsigned long int i, ls_bit, ls_mask = 1;

/*
 * Extract the integer stored
 */
	*cursor_loop_max = *cursor_loop_max + no_of_bits * bit_gap;
	for( integer_stored=0; *cursor_postion < *cursor_loop_max ; (*cursor_postion)++ ){
		tmp_char1 = fgetc( carrier_file );
		ls_bit = tmp_char1 & ls_mask;
		integer_stored = (integer_stored << 1) | ls_bit;
	/*
	 * skip the some space if bit_gap > 1
	 */
		for(i=0; i < (bit_gap -1); i++){
			fgetc( carrier_file );
		}
	}
	return integer_stored;
}

char extract_character_from_carrier_file( FILE *carrier_file, unsigned long int *cursor_postion,
		unsigned long int *cursor_loop_max, unsigned long int bit_gap ){
/*
 * Variable declaration to store partial results
 */
	char character_stored;

/*
 * Temporary variable declarations
 */
	char tmp_char1;
	unsigned long int i, ls_bit, ls_mask = 1;

/*
 * Extract the Character stored
 */
	*cursor_loop_max = *cursor_loop_max + 8 * sizeof(char) * bit_gap;
	for( character_stored=0; *cursor_postion < *cursor_loop_max ; (*cursor_postion)++ ){
		tmp_char1 = fgetc( carrier_file );
		ls_bit = tmp_char1 & ls_mask;
		character_stored = (character_stored << 1) | ls_bit;
	/*
	 * skip the some space if bit_gap > 1
	 */
		for(i=0; i < (bit_gap -1); i++, (*cursor_postion)++ ){
			fgetc( carrier_file );
		}
	}
	return character_stored;
}

