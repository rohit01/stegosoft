/*
 * stegno_encrypt_header.c
 *
 *  Created on: May 1, 2011
 *      Author: Rohit Gupta
 *  Program to Hide Message in a wav audio file.
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

int write_integer_in_output_file(unsigned long int int_variable, FILE *master_file, FILE *output_file, unsigned long int number_of_bits,
		unsigned long int bit_gap, unsigned long int *cursor_position, unsigned long int *cursor_loop_max);
int write_character_in_output_file(unsigned char char_variable, FILE *master_file, FILE *output_file,
		unsigned long int bit_gap, unsigned long int *cursor_position, unsigned long int *cursor_loop_max);
unsigned long int extract_filename_index_from_full_path(char *file);

int main( int no_of_arguments, char *cmd_line_arguments[] ){
/*
 * Information in Arguments:
 * 1. Master Filename (Full path or relative)
 * 2. Output Folder Full Path
 * 3. No of message files
 * 4. Encrypt All
 * 5. password
 * 6. Serially all message file details in the following order:
 * 6.a. File_size
 *   b. Filename_size
 *   c. Encryption
 *   d. Filename
 *
 */

	char *master_filename, *output_filename_full_path, *password;
	unsigned long int master_filesize, no_of_message_files, encrypt_all, password_size, header_size, bit_gap, total_message_filesize, version=1;
	message_header_structure  *message_details;
	FILE *master_file, *message_file, *output_file;

/*
 *  Temporary variable declarations:
 */
	unsigned char tmp_char1;
	unsigned long int i, j, tmp_int, cursor_position, cursor_loop_max, ms_bit, ms_mask, ls_mask;

	master_filename = cmd_line_arguments[1];

/*
 * Find the size of Master File and
 * initialize the master_filesize variable
 */
	master_file  = fopen( master_filename  ,"r");
	fseek( master_file, 0, SEEK_END);
	master_filesize = ftell( master_file );
	fclose( master_file );

/*
 * Allocate memory for output_filename_full_path
 * and initialize the variable
 */
	output_filename_full_path = malloc( sizeof(char) * ( strlen(cmd_line_arguments[2]) + 1) );
	strcpy(output_filename_full_path, cmd_line_arguments[2]);

	no_of_message_files = atoi(cmd_line_arguments[3]);
	encrypt_all = atoi(cmd_line_arguments[4]);
	password = cmd_line_arguments[5];
	password_size = strlen(password);

/*
 * Allocate Memory for message_details for required
 * number of files
 */
	message_details = calloc( no_of_message_files, sizeof(message_header_structure) );

/*
 * Initialize the values for all items in message_details dynamic array
 */
	for(i=0; i < no_of_message_files; i++) {
		message_details[i].file_size = atoi( cmd_line_arguments[ 6+4*i ] );
		message_details[i].filename_size = atoi( cmd_line_arguments[ 7+4*i ] );
		message_details[i].encryption = atoi( cmd_line_arguments[ 8+4*i ] );
       /*
	* Allocate memory to store filename in filename pointer
	*/
		message_details[i].filename = calloc( strlen( cmd_line_arguments[ 9+4*i ] ) + 1, sizeof(char) );
		strcpy(message_details[i].filename, cmd_line_arguments[ 9+4*i ] );
	}

/*
 * Find Header Length to be stored
 */
	header_size = 48;
	if( encrypt_all != 0 ){
		header_size = header_size + 16 + password_size*8;
	}
	for(i=0; i<no_of_message_files; i++){
		header_size = header_size + 44 + 8 * message_details[i].filename_size ;
	}

/*
 * Find the required bit gap
 */
	total_message_filesize = 0;
	for(i=0; i<no_of_message_files; i++){
		total_message_filesize = total_message_filesize + message_details[i].file_size ;
	}
	tmp_int = master_filesize - ( header_size + 50 + 1);
	bit_gap = tmp_int / (total_message_filesize * 8) ;
	if (bit_gap >= 256 ){
		bit_gap = 255;
	}
	else if(bit_gap <= 0){
		return 1;
	}

/*
 * Now inserting the header in the output file with
 * the help of master file
 */

/*
 * Now open the master and output file
 */
	master_file  = fopen( master_filename  ,"r");
	output_file  = fopen( output_filename_full_path  ,"w");

/*
 * Leaving space (first 50 bytes) for wav format header.
 */
	cursor_position=0;
	cursor_loop_max = 50;
	for( ; cursor_position < cursor_loop_max; cursor_position++){
		tmp_char1 = fgetc(master_file);
		fputc(tmp_char1, output_file);
	}

/*
 * Inserting the Main Header information
 * -------------------------------------
 * Insert version as (0001)base2 = (1)base10
 * number of bits = 4
 */
	write_integer_in_output_file(version, master_file, output_file, 4, 1, &cursor_position, &cursor_loop_max);

/*
 * Insert Header Size (24 bits)
 */
	write_integer_in_output_file(header_size, master_file, output_file, 24, 1, &cursor_position, &cursor_loop_max);

/*
 * Insert Bit Gap (8 bits)
 */
	write_integer_in_output_file(bit_gap, master_file, output_file, 8, 1, &cursor_position, &cursor_loop_max);

/*
 * Insert Encrypt All (4 bits)
 */
	write_integer_in_output_file(encrypt_all, master_file, output_file, 4, 1, &cursor_position, &cursor_loop_max);

/*
 * Insert No. of Message files (8 bits)
 */
	write_integer_in_output_file(no_of_message_files, master_file, output_file, 8, 1, &cursor_position, &cursor_loop_max);

/*
 * Insert Password size and Password
 * if Encrypt all is enabled
 */
	if( encrypt_all != 0 ){
		password_size = strlen( password );
	/*
	 * password size is 16 bits, so the number must be < 65535
	 * Insert Password size
	 */
		write_integer_in_output_file(password_size, master_file, output_file, 16, 1, &cursor_position, &cursor_loop_max);
	/*
	 * Now insert password in character mode
	 */
		for(i=0; i < password_size ; i++){
			write_character_in_output_file(password[i], master_file, output_file, 1, &cursor_position, &cursor_loop_max);
		}
	}

/*
 * Inserting the optional header information
 * -----------------------------------------
 */
	for(i=0; i < no_of_message_files; i++){
	/*
	 * Insert ith message file size, Filename size, encryption
	 */
		write_integer_in_output_file(message_details[i].file_size, master_file, output_file, 32, 1, &cursor_position, &cursor_loop_max);
		write_integer_in_output_file(message_details[i].filename_size, master_file, output_file, 8, 1, &cursor_position, &cursor_loop_max);
		write_integer_in_output_file(message_details[i].encryption, master_file, output_file, 4, 1, &cursor_position, &cursor_loop_max);
	/*
	 * Insert Message Filename /only filename and not full path/
	 */
		j = extract_filename_index_from_full_path( message_details[i].filename );
		for( ; message_details[i].filename[j] != '\0' ; j++){
			write_character_in_output_file(message_details[i].filename[j], master_file, output_file, 1, &cursor_position, &cursor_loop_max);
		}
	}
/*
 * --------------------------
 * Header information stored
 * --------------------------
 */

/*
 * Inserting the Message files one by one
 * in sequence by using loop
 */
	for(i=0; i < no_of_message_files; i++){
		message_file = fopen( message_details[i].filename, "r" );
		for(j=0; j < message_details[i].file_size; j++){
			tmp_char1 = fgetc( message_file );
			write_character_in_output_file( tmp_char1, master_file, output_file, bit_gap, &cursor_position, &cursor_loop_max);
		}
		fclose(message_file);
	}

/*
 * Copying the rest of audio (wav) file
 * in its original form
 */
	cursor_loop_max = master_filesize;
	for( ; cursor_position < cursor_loop_max; cursor_position++){
		tmp_char1 = fgetc(master_file);
		fputc(tmp_char1, output_file);
	}

/*
 * Close open Files
 */
	fclose(master_file);
	fclose(output_file);

/*
 * free allocated memories used for storing
 * header information
 */
	for(i=0; i < no_of_message_files; i++){
		free( message_details[i].filename );
	}
	free( message_details );
	free( output_filename_full_path );

	return 0;

}

int write_integer_in_output_file(unsigned long int int_variable, FILE *master_file, FILE *output_file, unsigned long int number_of_bits,
		unsigned long int bit_gap, unsigned long int *cursor_position, unsigned long int *cursor_loop_max){

	unsigned long int i, ms_mask, ms_bit, tmp_int;
	unsigned char tmp_char1;

	// calculate Most Significant Bit mask (ms_mask).
	i=1;
	while(i != 0){
		ms_mask = i;
		i <<= 1;
	 }

	tmp_int = int_variable;
	for(i=0 ; i < ((sizeof(tmp_int)*8 - number_of_bits)); i++){
		tmp_int <<= 1;
	}

	*cursor_loop_max += number_of_bits * bit_gap;
	for( ; *cursor_position < *cursor_loop_max; *cursor_position = (*cursor_position)++){
		tmp_char1 = fgetc( master_file );
		ms_bit = tmp_int & ms_mask;
		if( ms_bit == 0 ){
			ms_bit = 0;
		}
		else{
			ms_bit = 1;
		}
		tmp_int <<= 1;
		tmp_char1 = (tmp_char1 & (-2)) | ms_bit;
		fputc( tmp_char1, output_file);
	/*
	 * Provide Bit gap if bit_gap > 1
	 */
		for( i=0; i<(bit_gap-1); i++, (*cursor_position)++){
			tmp_char1 = fgetc(master_file);
			fputc(tmp_char1, output_file);
		}
	}

	return 0;
}

int write_character_in_output_file(unsigned char char_variable, FILE *master_file, FILE *output_file,
		unsigned long int bit_gap, unsigned long int *cursor_position, unsigned long int *cursor_loop_max){

	unsigned char i, tmp_char1, ms_mask, ms_bit;

	// calculate Most Significant Bit mask (ms_mask).
	i=1;
	while(i != 0){
		ms_mask = i;
		i <<= 1;
	 }

	*cursor_loop_max += 8 * sizeof(char) * bit_gap;
	for( ; *cursor_position < *cursor_loop_max; *cursor_position = (*cursor_position)++){
		tmp_char1 = fgetc( master_file );
		ms_bit = char_variable & ms_mask;
		if( ms_bit == 0 ){
			ms_bit = 0;
		}
		else{
			ms_bit = 1;
		}
		char_variable <<= 1;
		tmp_char1 = (tmp_char1 & (-2)) | ms_bit;
		fputc( tmp_char1, output_file);

	/*
	 * Provide Bit gap if bit_gap > 1
	 */
		for( i=0; i<(bit_gap-1); i++, (*cursor_position)++){
			tmp_char1 = fgetc(master_file);
			fputc(tmp_char1, output_file);
		}
	}
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
