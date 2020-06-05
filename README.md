# SEGY reader

### 
Designed to be a very light weight seismic reader that is easy and flexible.  

Because of the history of SEGY standard there have been lots of places
 where people tended to use as default byte possitions and data formats,
 For that reason we do minimal (no) checking to make sure the bit possitions have 
 the information that is expected.  
 
We instead rely on highly flexable configuration files.
the defaule segy 1 and segy 0 files can be extened and adapted with custom config files.
If there is something that is missing that is needed you can use a constant and it will override whatever
is in the byte possitions.  
