#include <boost/python.hpp>
#include <iostream>
#include <string>
#include <iomanip>
#include <scitbx/array_family/flex_types.h>

namespace py = boost::python;
using scitbx::af::flex_double;
using scitbx::af::flex_grid;
using scitbx::af::flex_int;

std::string img_arr_2_str(flex_double& data2d)
{
    /*
     * Here we generate a very long string
     * that contains and entire JSON file
     * with the dimensions (d1, d2) and
     * the array in "str_data"
     */
    int d1 = data2d.accessor().all()[0];
    int d2 = data2d.accessor().all()[1];
    int i, j, pos, pos_size;
    double d_num;
    char std_str[15];
    int buff_size = d1 * d2 * 15 + 30;
    std::cout << "buff_size =" << buff_size << "\n";
    // creating a char buffer full of spaces
    char * ch_buff;
    ch_buff = new char[buff_size];
    memset(ch_buff,' ',buff_size);
    //pos will keep track of where to write next
    pos = 0;
    // first writing in memory string, starting with << { >>
    strcpy(&ch_buff[pos], "{");
    pos++;
    // writing the << d1 >> field in JSON format, dimension #1
    pos_size = sprintf( std_str, "\"d1\":%i,", d1);
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;
    // writing the << d2 >> field in JSON format, dimension #2
    pos_size = sprintf( std_str, "\"d2\":%i,", d2);
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;
    // writing the left side of << str_data >> field
    pos_size = sprintf( std_str, "\"str_data\":\"");
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;

    // all pixel intensities should be written with a loop
    std::cout << "looping thru (" << d1 << ", " << d2 << ") ... nums \n";
    for (i = 0; i < d1; i++) {
        for (j = 0; j < d2; j++) {
            // writing intensity
            d_num = double(data2d(i, j));
            pos_size = sprintf( std_str, "%.2f", d_num);
            strcpy(&ch_buff[pos], std_str);
            pos = pos + pos_size;
            // writing coma
            strcpy(&ch_buff[pos], ",");
            pos++;
        }
    }
    std::cout << "... Loop END\n";

    // moving backwards to overwrite last coma
    pos--;
    // closing both: quotes and braces
    pos_size = sprintf( std_str, "\"}");
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;
    // passing all char buffer to a std::string to returning it
    std::string all_str((char *)ch_buff);
    // clearing memory
    delete ch_buff;
    return all_str;
}

std::string slice_arr_2_str( flex_double& data2d,
                             int inv_scale,
                             int x1, int y1,
                             int x2, int y2 )
{
    int d1 = data2d.accessor().all()[0];
    int d2 = data2d.accessor().all()[1];
    int x, y, pos, pos_size, dx, dy;
    int scaled_dx, scaled_dy;

    std::cout << "\n inv_scale ="<< inv_scale << " \n";
    if(x1 >= d1 or x2 > d1 or  x1 < 0 or x2 <= 0 or
       y1 >= d2 or y2 > d2 or  y1 < 0 or y2 <= 0 or
       x1 > x2 or y1 > y2
    ){
        std::cout << "\n ***  array bounding error  *** \n";
        std::cout << "(x1, y1, x2, y2) = " << x1 << ", " << y1 << ", "
                                           << x2 << ", " << y2 << "\n";
        std::cout << "d1[bound], d2[bound] = " << d1 << ", " << d2 << "\n";
        return "Error";
    };

    double d_num;
    char std_str[15];
    dx = x2 - x1;
    dy = y2 - y1;
    std::cout << "dx, dy  = " << dx << "," << dy << "\n";
    int buff_size = dx * dy * 15 + 30;
    std::cout << "buff_size =" << buff_size << "\n";
    std::cout << "x1, y1, x2, y2 = " << x1 << "," << y1 << "," <<
                                        x2 << "," << y2 << "," << "\n";
    char * ch_buff;
    ch_buff = new char[buff_size];
    memset(ch_buff,' ',buff_size);
    pos = 0;
    strcpy(&ch_buff[pos], "{");
    pos++;

    pos_size = sprintf( std_str, "\"str_data\":\"");
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;

    std::cout << "looping thru (" << x2 - x1 << ", " << y2 - y1
                                  << ") ... nums \n";

    int mini_x, mini_y;
    double d_tot, mini_count;
    scaled_dx = 0;
    for (x = x1; x < x2; x = x + inv_scale) {
        scaled_dy = 0;
        for (y = y1; y < y2; y = y + inv_scale) {
            // d_num = double(data2d(x, y));
            d_tot = 0;
            mini_count = 0;
            for (mini_x = x; mini_x < x + inv_scale; mini_x++) {
                for (mini_y = y; mini_y < y + inv_scale; mini_y++) {
                    d_tot = d_tot + double(data2d(mini_x, mini_y));
                    mini_count++;
                }
            }
            d_num = d_tot / mini_count;
            if(isnan(d_num)){
                d_num = 0;
            }

            /* only needed for debugging
            std::cout << "d_num = " << d_num << ", d_tot = " << d_tot <<
                         ", mini_count = " << mini_count << "\n";
            */

            pos_size = sprintf( std_str, "%.2f", d_num);
            strcpy(&ch_buff[pos], std_str);
            pos = pos + pos_size;
            strcpy(&ch_buff[pos], ",");
            pos++;
            scaled_dy++;
        }
        scaled_dx++;
    }
    std::cout << "... Loop END\n scaled_dx, scaled_dy ="
              << scaled_dx << ", " << scaled_dy << " \n";
    pos--;

    pos_size = sprintf( std_str, "\",");
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;

    pos_size = sprintf( std_str, "\"d1\":%i,", scaled_dx);
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;

    pos_size = sprintf( std_str, "\"d2\":%i", scaled_dy);
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;

    pos_size = sprintf( std_str, "}");
    strcpy(&ch_buff[pos], std_str);
    pos = pos + pos_size;
    std::string all_str((char *)ch_buff);
    delete ch_buff;
    return all_str;
}

BOOST_PYTHON_MODULE(img_stream_ext)
{
    using namespace boost::python;
    def("img_arr_2_str", img_arr_2_str);
    def("slice_arr_2_str", slice_arr_2_str);
}
