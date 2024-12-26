 /* Copyright (C) 2012 Realtek Semiconductor Corp.
 * All Rights Reserved.
 *
 * This program is the proprietary software of Realtek Semiconductor
 * Corporation and/or its licensors, and only be used, duplicated,
 * modified or distributed under the authorized license from Realtek.
 *
 * ANY USE OF THE SOFTWARE OTHER THAN AS AUTHORIZED UNDER
 * THIS LICENSE OR COPYRIGHT LAW IS PROHIBITED.
 *
 * Purpose : Definition of Switch Global API
 *
 * Feature : The file have include the following module and sub-modules
 *           (1) Switch parameter settings
 *
 */


/*
 * Include Files
 */
#include <dal_rtl8373_switch.h>
#include <rtl8373_asicdrv.h>
#include <dal_rtl8373_drv.h>
#include <string.h>

/*
 * Symbol Definition
 */
#ifndef ENABLE
#define ENABLE 1
#endif
    
#ifndef DISABLE
#define DISABLE 0
#endif

#define  PHY_PATCH 1

/*
 * Data Declaration
 */

rtk_uint32 currentVersion, FWVersion;

chip_mode_type_t CHIP_TYPE;


rtk_uint16 an_10p3125g[][3] ={
       {0x21 ,0x10, 0x4480} ,{0x21, 0x13 ,0x0400}, {0x21, 0x18, 0x6c02}, {0x21 ,0x18,0x6d02} ,
            {0x21, 0x1b, 0x424e}, {0x21, 0x1d ,0x0002} ,{0x36 ,0x1c ,0x1390} ,{0x2e ,0x9  ,0x0601} ,
            {0x2e, 0xb  ,0x232c}, {0x2e, 0xc  ,0xA217}, {0x2e ,0x16, 0x0443}, {0x2e, 0x1d, 0xabb0} ,
            {0x2e ,0x4,  0x80  } ,{0x2e, 0x6  ,0x408 } ,{0x2e ,0x7 , 0x20d } ,{0x2e, 0xb , 0x222c} ,{0x2e, 0xd , 0xFE40}
};

   
rtk_uint16  an_3p125g[][3]= {
      {0x21, 0x10, 0x6480}, {0x21, 0x13 ,0x400 }, {0x21, 0x18 ,0x6d02}, {0x21 ,0x1b ,0x424e},
      {0x21 ,0x1d ,0x2   } ,{0x36 ,0x1c ,0x1390}, {0x28, 0x4  ,0x0080}, {0x28, 0x9  ,0x601 },
      {0x28 ,0xb , 0x232c} ,{0x28, 0xc,  0x9217} ,{0x28 ,0xf,  0x5b50}, {0x28, 0x16, 0x443 },
      {0x28, 0x1d, 0xabb0}
};
rtk_uint16 an_1p25g[][3]= {
      {0x21, 0x10, 0x6480}, {0x21 ,0x13 ,0x0400}, {0x21 ,0x18 ,0x6d02}, {0x21, 0x1b ,0x424e},
      {0x21, 0x1d, 0x0002}, {0x36 ,0x1c, 0x1390} ,{0x24 ,0x04 ,0x0080}, {0x24 ,0x09, 0x0601},
      {0x24 ,0x0b, 0x232c}, {0x24, 0x0c ,0x9217}, {0x24 ,0x0f ,0x5B50} ,{0x24 ,0x16, 0x0443},
      {0x24, 0x1d ,0xabb0}
};
rtk_uint16 dig_patch_mac[][3]=  {
      {6 , 18 ,0x5078}, {7,  6  ,0x9401}, {7 , 8 , 0x9401}, {7  ,10 ,0x9401},
      {7 , 12 ,0x9401}, {31 ,11 ,0x0003} 
};
rtk_uint16 dig_patch_phy[1][3]= {
      {6,  18 ,0x5078} 
};


rtk_uint16 patch_list[][2]=
{
    {0xC202, 0xC1} ,
    {0xC203, 0x01},
    {0xC204, 0xFF} ,
    {0xC205, 0x02},
    {0xC206, 0x6A}, 
    {0xC207, 0x02}  , 
    {0xC208, 0xD9} ,
    {0xC209, 0x03}  , 
    {0xC20A, 0x5C} ,
    {0xC20B, 0x03}  , 
    {0xC20C, 0xF6}, 
    {0xC20D, 0x04}  , 
    {0xC20E, 0x88}, 
    {0xC20F, 0x05}  , 
    {0xC210, 0x40}, 
    {0xC211, 0x06}  , 
    {0xC212, 0x3D}, 
    {0xC213, 0x07}  , 
    {0xC214, 0x24}, 
    {0xC215, 0x08}  , 
    {0xC216, 0x2B}, 
    {0xC217, 0x09}  , 
    {0xC218, 0x84}, 
    {0xC219, 0x0B}  , 
    {0xC21A, 0x41}, 
    {0xC21B, 0x0C}  , 
    {0xC21C, 0x44}, 
    {0xC21D, 0x0E}  , 
    {0xC21E, 0x00}, 
    {0xC21F, 0xF6}  ,                 
    {0xC220, 0xF6},
    {0xC221, 0xF5},
    {0xC222, 0xF3},
    {0xC223, 0xF3},
    {0xC224, 0xEF},
    {0xC225, 0xEB},
    {0xC226, 0xE7},
    {0xC227, 0xE4},
    {0xC228, 0xE2},
    {0xC229, 0xDF},
    {0xC22A, 0xDD},
    {0xC22B, 0xDB}, 
    {0xC22C, 0xDA},
    {0xC22D, 0xD9}, 
    {0xC270, 0x18}, 
    {0xC271, 0x19}, 
    {0xC272, 0x1C}, 
    {0xC273, 0x1E}, 
    {0xC274, 0x20}, 
    {0xC275, 0x21}, 
    {0xC276, 0x22}, 
    {0xC277, 0x23}, 
    {0xC278, 0x23}, 
    {0xC279, 0x24}, 
    {0xC27A, 0x25}, 
    {0xC27B, 0x25}, 
    {0xC27C, 0x26}, 
    {0xC27D, 0x26}, 
    {0xC27E, 0x26}, 
    {0xC27F, 0x4A}, 
    {0xC280, 0x4A}, 
    {0xC281, 0x4A}, 
    {0xC282, 0x4D}, 
    {0xC283, 0x4D}, 
    {0xC284, 0x50}, 
    {0xC285, 0x55}, 
    {0xC286, 0x52}, 
    {0xC287, 0x52}, 
    {0xC288, 0x52}, 
    {0xC289, 0x52}, 
    {0xC28A, 0x52}, 
    {0xC28B, 0x51}, 
    {0xC28C, 0x52}, 
    {0xC28D, 0x52}, 
    {0xC201, 0x01}, 
    {0xC22E, 0xD7}, 
    {0xC26F, 0x18}, 
    {0xC28E, 0x52}, 
};

rtk_uint16 alg_tune_giga_220411_patch[][2]=
{
    {0x80b5,0x98},
    {0x80b6, 0xc3} ,
    {0x80b7 ,0xf6} ,
    {0x80b8 ,0x04},
    {0x80b9 ,0xd2},
    {0x80ba, 0x06},
    {0x80bb ,0xfa},
    {0x80bc ,0xbc},
    {0x80bd ,0x66},
    {0x80be ,0x19} ,
    {0x80bf ,0x2f} ,
    
    {0x80c9, 0xc0} ,
    {0x80ca ,0xbb},
    {0x80cb ,0xf6} ,
    {0x80cc ,0x04},
    {0x80cd ,0x9e} ,
    {0x80ce ,0x06} ,
    {0x80cf ,0xfa},
    {0x80d0, 0xc4},
    {0x80d1 ,0x63},
    {0x80d2 ,0x19},
    {0x80d3 ,0x2f} ,      
    {0x80c0, 0x0c},
    {0x80d4 ,0x0c}
};

rtk_uint16 alg_tune_fnet_6818_220414_patch[][2]=
{
    {0x80a1 ,0x50},
    {0x80a2 ,0x9c},
    {0x80a3 ,0xb6},
    {0x80a4 ,0x03},
    {0x80a5 ,0xda} ,
    {0x80a6 ,0x0a},
    {0x80a7 ,0xed},
    {0x80a8 ,0xa6},
    {0x80a9, 0xe4},
    {0x80aa ,0x1f},
    {0x80ab ,0x3b},
    {0x80ac ,0x1e}   
};



/*
 * Function Declaration
 */



void delay_loop(rtk_uint32 loop)
{
    rtk_uint32 i, j;

    for (i = 0; i < loop; ++i)
        for (j = 0; j < 400; j++)
            ;
}


void Pin_Reset_8224_via_8373()
{

    rtl8373_setAsicRegBit(RTL8373_GPIO_OUT1_ADDR, 4, 0);
    rtl8373_setAsicRegBit(RTL8373_GPIO_OE1_ADDR, 4, 1);
  
  // after 11
  delay_loop(100);
  //  wdbs_6818 0x40 4 4 0; //GPIO_OUT1.bit4=1 for GPIO36=1 to set RTL8224 nRESET pin high
  //setRegBits(RTL8371C_GPIO_OUT1_ADDR , 4, 4, 1);  //GPIO_OUT1.bit4=1 for GPIO36=1 to set RTL8224 nRESET pin high
  rtl8373_setAsicRegBit(RTL8373_GPIO_OUT1_ADDR, 4, 1);
  //  after 50; //delay 50ms for RTL8224 power on sequece finish
  delay_loop(500);
}


void uc1_sram_write_8b(rtk_uint32 port,rtk_uint32 addr,rtk_uint32 val)
{
    //setPhyMaskRegBits(1<<port,31,0xa436,15,0,addr);
    //setPhyMaskRegBits(1<<port,31,0xa438,15,8,val);
    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, addr);
    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xff<<8, val);
}

rtk_uint32 uc1_sram_read_8b(rtk_uint32 port,rtk_uint32 addr)
{
    rtk_uint32 regdata;
    
    //setPhyMaskRegBits(1<<port,31,0xa436,15,0,addr);
    //return getphyRegBits(1<<port,31,0xa438,15,8);
    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, addr);
    dal_rtl8373_phy_regbits_read(1<<port, 31, 0xa438, 0xff<<8, &regdata);

    return regdata;
}

void uc2_sram_write_8b(rtk_uint32 port,rtk_uint32 addr,rtk_uint32 val)
{
    //setPhyMaskRegBits(1<<port,31,0xb87c,15,0,addr);
    //setPhyMaskRegBits(1<<port,31,0xb87e,15,8,val);
    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb87c, 0xffff, addr);
    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb87e, 0xff<<8, val);
}

rtk_uint32 uc2_sram_read_8b(rtk_uint32 port,rtk_uint32 addr)
{
    rtk_uint32 regdata;
    
    //setPhyMaskRegBits(1<<port,31,0xb87c,15,0,addr);
    //return getphyRegBits(1<<port,31,0xb87e,15,8);

    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb87c, 0xffff, addr);
    dal_rtl8373_phy_regbits_read(1<<port, 31, 0xb87e, 0xff<<8, &regdata);

    return regdata;
}

void data_ram_write_8b (rtk_uint32 port, rtk_uint32 addr,rtk_uint32 val)
{
    /*setPhyMaskRegBits(1<<port, 31, 0xB88E ,15, 0,  addr);
    if (addr % 2) {
        setPhyMaskRegBits(1<<port, 31,0xB890, 7,  0 , val);
    } else {
        setPhyMaskRegBits(1<<port, 31,0xB890 ,15 ,8  , val);
    }*/

    dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb88e, 0xffff, addr);
    
    if(addr % 2)
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xB890, 0xff, val);
    else
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xB890, 0xff<<8, val);
}




rtk_uint16 rst_smtr_patch_6818B_220609_patch[][2]=
{
        {0xa436,0xA016} ,{0xa438 ,0x0000} ,{0xa436,0xA012} ,{0xa438 ,0x0000},
        {0xa436,0xA014} ,{0xa438 ,0x1800} ,{0xa438 ,0x8010} ,{0xa438 ,0x1800},
        {0xa438 ,0x8018} ,{0xa438 ,0x1800} ,{0xa438 ,0x8018} ,{0xa438 ,0x1800},
        {0xa438 ,0x8018} ,{0xa438 ,0x1800} ,{0xa438 ,0x8018} ,{0xa438 ,0x1800},
        {0xa438 ,0x8018} ,{0xa438 ,0x1800} ,{0xa438 ,0x8018} ,{0xa438 ,0x1800},
        {0xa438 ,0x8018} ,{0xa438 ,0xd711} ,{0xa438 ,0x8808} ,{0xa438 ,0x404f},
        {0xa438 ,0xa808} ,{0xa438 ,0x4050} ,{0xa438 ,0x8808} ,{0xa438 ,0x1800},
        {0xa438 ,0x1e13} ,{0xa436,0xA026} ,{0xa438 ,0xffff} ,{0xa436,0xA024},
        {0xa438 ,0xffff} ,{0xa436,0xA022} ,{0xa438 ,0xffff} ,{0xa436,0xA020},
        {0xa438 ,0xffff} ,{0xa436,0xA006} ,{0xa438 ,0xffff} ,{0xa436,0xA004},
        {0xa438 ,0xffff} ,{0xa436,0xA002} ,{0xa438 ,0xffff} ,{0xa436,0xA000},
        {0xa438 ,0x1e10} ,{0xa436,0xA008} ,{0xa438 ,0x0100}  
};
void rst_smtr_patch_6818B_220609 (rtk_uint32 phymask)
{

    rtk_uint16 port,i,addr,val,len;
    rtk_uint32 regdata;

    len= sizeof(rst_smtr_patch_6818B_220609_patch)/4;
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            for(i=0;i<len;i++)
            {
                addr=rst_smtr_patch_6818B_220609_patch[i][0];
                val=rst_smtr_patch_6818B_220609_patch[i][1];    


                dal_rtl8373_phy_write(1<<port, 31, addr, val);
                dal_rtl8373_phy_read(port, 31, addr, &regdata);
            }    
        }
    }
    
}


rtk_uint16 n2_tp3_patch_6818B_220610_patch[][2]=
{
        {0xa436,0xA016} ,{0xa438 ,0x0020} ,{0xa436,0xA012} ,{0xa438 ,0x0000},
        {0xa436,0xA014} ,{0xa438 ,0x1800} ,{0xa438 ,0x8010} ,{0xa438 ,0x1800},
        {0xa438 ,0x8027} ,{0xa438 ,0x1800} ,{0xa438 ,0x8027} ,{0xa438 ,0x1800},
        {0xa438 ,0x8027} ,{0xa438 ,0x1800} ,{0xa438 ,0x8027} ,{0xa438 ,0x1800},
        {0xa438 ,0x8027} ,{0xa438 ,0x1800} ,{0xa438 ,0x8027} ,{0xa438 ,0x1800},
        {0xa438 ,0x8027} ,{0xa438 ,0xa710} ,{0xa438 ,0xa00a} ,{0xa438 ,0x8190},
        {0xa438 ,0x8204} ,{0xa438 ,0x8280} ,{0xa438 ,0xa404} ,{0xa438 ,0xd130},
        {0xa438 ,0xd047} ,{0xa438 ,0x1000} ,{0xa438 ,0x0b46} ,{0xa438 ,0xd700},
        {0xa438 ,0x5fb4} ,{0xa438 ,0xa110} ,{0xa438 ,0xa204} ,{0xa438 ,0xa280},
        {0xa438 ,0xd130} ,{0xa438 ,0xd047} ,{0xa438 ,0x1000} ,{0xa438 ,0x0b46},
        {0xa438 ,0xd700} ,{0xa438 ,0x5fb4} ,{0xa438 ,0x1800} ,{0xa438 ,0x0505},
        {0xa436,0xA10E} ,{0xa438 ,0xffff} ,{0xa436,0xA10C} ,{0xa438 ,0xffff},
        {0xa436,0xA10A} ,{0xa438 ,0xffff} ,{0xa436,0xA108} ,{0xa438 ,0xffff},
        {0xa436,0xA106} ,{0xa438 ,0xffff} ,{0xa436,0xA104} ,{0xa438 ,0xffff},
        {0xa436,0xA102} ,{0xa438 ,0xffff} ,{0xa436,0xA100} ,{0xa438 ,0x04ff},
        {0xa436,0xA110} ,{0xa438 ,0x0001}     
};
void n2_tp3_patch_6818B_220610 (rtk_uint32 phymask)
{
    rtk_uint32 port,i,addr,val,len;

    len= sizeof(n2_tp3_patch_6818B_220610_patch)/4;
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
             for(i=0;i<len;i++)
             {
                addr=n2_tp3_patch_6818B_220610_patch[i][0];
                val=n2_tp3_patch_6818B_220610_patch[i][1]; 

                dal_rtl8373_phy_write(1<<port, 31, addr, val);
                              
             }    
        }
    }
    
}


rtk_uint16 uc2_patch_6818B_220614_patch[][2]=
{
        {0xa436, 0xb87c}, {0xa438,0x858b}, {0xa436, 0xb87e}, {0xa438,0xaf85},
        {0xa438,0xa3af}, {0xa438,0x8660}, {0xa438,0xaf86}, {0xa438,0x85af},
        {0xa438,0x8690}, {0xa438,0xaf87}, {0xa438,0x29af}, {0xa438,0x8729},
        {0xa438,0xaf87}, {0xa438,0x68af}, {0xa438,0x87ab}, {0xa438,0xe18f},
        {0xa438,0xff39}, {0xa438,0x019e}, {0xa438,0x64e0}, {0xa438,0x8397},
        {0xa438,0xe182}, {0xa438,0x001b}, {0xa438,0x019f}, {0xa438,0x07ee},
        {0xa438,0x838c}, {0xa438,0x05af}, {0xa438,0x865d}, {0xa438,0xd10f},
        {0xa438,0xbf62}, {0xa438,0x0e02}, {0xa438,0x5f0a}, {0xa438,0xbf61},
        {0xa438,0xf902}, {0xa438,0x5f29}, {0xa438,0xe583}, {0xa438,0x8fbf},
        {0xa438,0x620b}, {0xa438,0x0265}, {0xa438,0xf9bf}, {0xa438,0x6211},
        {0xa438,0x0265}, {0xa438,0xf9bf}, {0xa438,0x6214}, {0xa438,0x0265},
        {0xa438,0xf0d1}, {0xa438,0x03bf}, {0xa438,0x61f9}, {0xa438,0x025f},
        {0xa438,0x0ae1}, {0xa438,0x8201}, {0xa438,0xbf62}, {0xa438,0x1702},
        {0xa438,0x5f0a}, {0xa438,0xbf62}, {0xa438,0x1a02}, {0xa438,0x65f9},
        {0xa438,0xbf62}, {0xa438,0x1a02}, {0xa438,0x65f0}, {0xa438,0xbf62},
        {0xa438,0x1d02}, {0xa438,0x65f9}, {0xa438,0xbf62}, {0xa438,0x1d02},
        {0xa438,0x65f0}, {0xa438,0xee83}, {0xa438,0x8c02}, {0xa438,0xaf86},
        {0xa438,0x5dd1}, {0xa438,0x0fbf}, {0xa438,0x620e}, {0xa438,0x025f},
        {0xa438,0x0abf}, {0xa438,0x61f9}, {0xa438,0x025f}, {0xa438,0x29e5},
        {0xa438,0x838f}, {0xa438,0xbf62}, {0xa438,0x0b02}, {0xa438,0x65f9},
        {0xa438,0xbf62}, {0xa438,0x1102}, {0xa438,0x65f9}, {0xa438,0xbf62},
        {0xa438,0x1402}, {0xa438,0x65f0}, {0xa438,0xd103}, {0xa438,0xbf61},
        {0xa438,0xf902}, {0xa438,0x5f0a}, {0xa438,0xd140}, {0xa438,0xbf62},
        {0xa438,0x1702}, {0xa438,0x5f0a}, {0xa438,0xbf62}, {0xa438,0x1a02},
        {0xa438,0x65f9}, {0xa438,0xbf62}, {0xa438,0x1a02}, {0xa438,0x65f0},
        {0xa438,0xbf62}, {0xa438,0x1d02}, {0xa438,0x65f9}, {0xa438,0xbf62},
        {0xa438,0x1d02}, {0xa438,0x65f0}, {0xa438,0xee83}, {0xa438,0x8c02},
        {0xa438,0xaf50}, {0xa438,0x5be1}, {0xa438,0x8fff}, {0xa438,0xa101},
        {0xa438,0x0bee}, {0xa438,0x838c}, {0xa438,0x07ee}, {0xa438,0x8fff},
        {0xa438,0x00af}, {0xa438,0x8682}, {0xa438,0xe183}, {0xa438,0x94a1},
        {0xa438,0x0107}, {0xa438,0xee83}, {0xa438,0x8c05}, {0xa438,0xaf86},
        {0xa438,0x82ee}, {0xa438,0x838c}, {0xa438,0x03af}, {0xa438,0x50a4},
        {0xa438,0xee8f}, {0xa438,0xff01}, {0xa438,0xee83}, {0xa438,0x8c01},
        {0xa438,0xaf52}, {0xa438,0x99ee}, {0xa438,0x8029}, {0xa438,0x0eee},
        {0xa438,0x8ffe}, {0xa438,0x00ef}, {0xa438,0x021b}, {0xa438,0x03d1},
        {0xa438,0x001b}, {0xa438,0x10ac}, {0xa438,0x2d0f}, {0xa438,0xa200},
        {0xa438,0x06d7}, {0xa438,0x000e}, {0xa438,0xaf86}, {0xa438,0xddd7},
        {0xa438,0x0011}, {0xa438,0xaf86}, {0xa438,0xdda0}, {0xa438,0x010f},
        {0xa438,0xa201}, {0xa438,0x06d7}, {0xa438,0x0012}, {0xa438,0xaf86},
        {0xa438,0xddd7}, {0xa438,0x0015}, {0xa438,0xaf86}, {0xa438,0xdda0},
        {0xa438,0x020f}, {0xa438,0xa202}, {0xa438,0x06d7}, {0xa438,0x0017},
        {0xa438,0xaf86}, {0xa438,0xddd7}, {0xa438,0x001b}, {0xa438,0xaf86},
        {0xa438,0xddee}, {0xa438,0x8ffe}, {0xa438,0x01af}, {0xa438,0x4451},
        {0xa438,0x0244}, {0xa438,0x5fe0}, {0xa438,0x8028}, {0xa438,0xac20},
        {0xa438,0x09bf}, {0xa438,0x6259}, {0xa438,0x025f}, {0xa438,0x29ac},
        {0xa438,0x281f}, {0xa438,0xbf61}, {0xa438,0xe702}, {0xa438,0x5f29},
        {0xa438,0xef21}, {0xa438,0xbf61}, {0xa438,0xea02}, {0xa438,0x5f29},
        {0xa438,0xef31}, {0xa438,0xef02}, {0xa438,0x1b03}, {0xa438,0xa0ff},
        {0xa438,0x10a2}, {0xa438,0x0008}, {0xa438,0xd170}, {0xa438,0xaf44},
        {0xa438,0x4eaf}, {0xa438,0x444b}, {0xa438,0xd15f}, {0xa438,0xaf44},
        {0xa438,0x4ea0}, {0xa438,0xfe0d}, {0xa438,0xa200}, {0xa438,0x05d1},
        {0xa438,0x59af}, {0xa438,0x444e}, {0xa438,0xd14c}, {0xa438,0xaf44},
        {0xa438,0x4eaf}, {0xa438,0x4451}, {0xa438,0xa300}, {0xa438,0x08d6},
        {0xa438,0x469e}, {0xa438,0xd200}, {0xa438,0xaf45}, {0xa438,0x67a3},
        {0xa438,0x0113}, {0xa438,0xa200}, {0xa438,0x08d6}, {0xa438,0x3819},
        {0xa438,0xd200}, {0xa438,0xaf45}, {0xa438,0x67d6}, {0xa438,0x3be6},
        {0xa438,0xd201}, {0xa438,0xaf45}, {0xa438,0x67a3}, {0xa438,0x0213},
        {0xa438,0xa200}, {0xa438,0x08d6}, {0xa438,0x2c8f}, {0xa438,0xd200},
        {0xa438,0xaf45}, {0xa438,0x67d6}, {0xa438,0x2f94}, {0xa438,0xd201},
        {0xa438,0xaf45}, {0xa438,0x67d6}, {0xa438,0x25cb}, {0xa438,0xd201},
        {0xa438,0xaf45}, {0xa438,0x67ac}, {0xa438,0x3006}, {0xa438,0xbf83},
        {0xa438,0xc0af}, {0xa438,0x8774}, {0xa438,0xbf83}, {0xa438,0xc2ef},
        {0xa438,0x130c}, {0xa438,0x161f}, {0xa438,0x001a}, {0xa438,0x94d8},
        {0xa438,0x19d9}, {0xa438,0xef74}, {0xa438,0xbf83}, {0xa438,0xe2ef},
        {0xa438,0x130c}, {0xa438,0x161f}, {0xa438,0x001a}, {0xa438,0x94d8},
        {0xa438,0x19d9}, {0xa438,0xef64}, {0xa438,0xef03}, {0xa438,0xd30c},
        {0xa438,0x0266}, {0xa438,0x020c}, {0xa438,0x74ef}, {0xa438,0x30ac},
        {0xa438,0x3006}, {0xa438,0xd691}, {0xa438,0xb1af}, {0xa438,0x45c8},
        {0xa438,0xd688}, {0xa438,0x6faf}, {0xa438,0x45c8}, {0xa436, 0xb85e},
        {0xa438,0x4ffb}, {0xa436, 0xb860}, {0xa438,0x5094}, {0xa436, 0xb862},
        {0xa438,0x5295}, {0xa436, 0xb864}, {0xa438,0x4404}, {0xa436, 0xb886},
        {0xa438,0xffff}, {0xa436, 0xb888}, {0xa438,0x4530}, {0xa436, 0xb88a},
        {0xa438,0x458a}, {0xa436, 0xb88c}, {0xa438,0xffff}, {0xa436, 0xb838},
        {0xa438,0x006f}
};
void uc2_patch_6818B_220614 (rtk_uint32 phymask)
{ 
    rtk_uint32 port,i,addr,val,len;

    len= sizeof(uc2_patch_6818B_220614_patch)/4;
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            for(i=0;i<len;i++)
            {
                addr=uc2_patch_6818B_220614_patch[i][0];
                val=uc2_patch_6818B_220614_patch[i][1]; 
                dal_rtl8373_phy_write(1<<port, 31, addr, val);
                          
            }    
        }
    }
 
}


rtk_uint16 data_ram_patch_6818B_220616_patch[][2]=
{
        {0xC202,  0xFA} ,{0xC203 , 0x02} ,{0xC204,0x4D} ,{0xC205,0x02},
        {0xC206,0x81} ,{0xC207,0x03} ,{0xC208,0x30} ,{0xC209,0x03},  
        {0xC20A,0xB5} ,{0xC20B,0x04} ,{0xC20C,0x3A} ,{0xC20D,0x04},  
        {0xC20E,0xE7} ,{0xC20F,0x05} ,{0xC210,0xAC} ,{0xC211,0x06},  
        {0xC212,0x94} ,{0xC213,0x07} ,{0xC214,0x98} ,{0xC215,0x08},  
        {0xC216,0xD7} ,{0xC217,0x0A} ,{0xC218,0x5C} ,{0xC219,0x0C},  
        {0xC21A,0x5E} ,{0xC21B,0x0E} ,{0xC21C,0x01} ,{0xC21D,0x10},  
        {0xC21E,0x5E} ,{0xC21F,0xF6}  ,
        
        {0xC220,0xF6} ,{0xC221,0xF5} ,{0xC222,0xF3} ,{0xC223,0xF3},  
        {0xC224,0xEF} ,{0xC225,0xEB} ,{0xC226,0xE7} ,{0xC227,0xE4},
        {0xC228,0xE2} ,{0xC229,0xDF} ,{0xC22A,0xDD} ,{0xC22B,0xDB} , 
        {0xC22C,0xDA} ,{0xC22D,0xD9}  ,
        
        {0xC270,0x18} ,{0xC271,0x19} ,{0xC272,0x1C} ,{0xC273,0x1E},  
        {0xC274,0x20} ,{0xC275,0x21} ,{0xC276,0x22} ,{0xC277,0x23}, 
        {0xC278,0x23} ,{0xC279,0x24} ,{0xC27A,0x25} ,{0xC27B,0x25},  
        {0xC27C,0x26} ,{0xC27D,0x26} ,{0xC27E,0x26} ,{0xC27F,0x4A}, 
        
        {0xC280,0x4A} ,{0xC281,0x4A} ,{0xC282,0x4D} ,{0xC283,0x4D} ,
        {0xC284,0x50} ,{0xC285,0x55} ,{0xC286,0x52} ,{0xC287,0x52}  ,
        {0xC288,0x52} ,{0xC289,0x52} ,{0xC28A,0x52} ,{0xC28B,0x51} , 
        {0xC28C,0x52} ,{0xC28D,0x52}  ,
        
        {0xC201,0x01} ,{0xC22E,0xD7} ,{0xC26F,0x18} ,{0xC28E,0x52}  
};
void data_ram_patch_6818B_220616(rtk_uint32 phymask)
{ 
    rtk_uint32 port,i,data_ram_addr,data_ram_val,len;

    len= sizeof(data_ram_patch_6818B_220616_patch)/4;
    
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            //setPhyMaskRegBits(1<<port, 31, 0xb896, 0, 0,0);//#disable data_mem_auto_inc
            //setPhyMaskRegBits(1<<port, 31, 0xb892, 15, 8,0);

            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xb896, 1, 0);
            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xb892, 0xff00, 0);
            for(i=0;i<len;i++)
            {
                data_ram_addr=data_ram_patch_6818B_220616_patch[i][0];
                data_ram_val=data_ram_patch_6818B_220616_patch[i][1];    
                data_ram_write_8b(port,data_ram_addr,data_ram_val);
            
            }    
            //setPhyMaskRegBits(1<<port, 31, 0xb896, 0, 0,1);//# enable data_mem_auto_inc
            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xb896, 1, 1);
            uc2_sram_write_8b(port,0x8217,0x1e);
        }
    }
}


rtk_uint16 alg_tune_2p5G_6818B_220616_patch[][2]=
{
    {0x8066, 0x10} ,
    {0x8067 ,0x40},
    {0x8068, 0x0a},
    {0x8069, 0x40},
    {0x806e, 0x02} ,
    {0x806f, 0xa0} ,

    {0x8084 ,0x10}, 
    {0x8085 ,0x40} ,
    {0x8086 ,0x0a},
    {0x8087, 0x40},
    {0x808c ,0x02},
    {0x808d ,0xa0}
};
void alg_tune_2p5G_6818B_220616 (rtk_uint32 phymask)
{
    rtk_uint32 port,i,uc2_sram_addr,uc2_sram_val,len;

    len= sizeof(alg_tune_2p5G_6818B_220616_patch)/4;
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            uc1_sram_write_8b(port,0x8017,0x7);    
            for(i=0;i<len;i++)
            {
                uc2_sram_addr=alg_tune_2p5G_6818B_220616_patch[i][0];
                uc2_sram_val=alg_tune_2p5G_6818B_220616_patch[i][1];        
                uc2_sram_write_8b(port,uc2_sram_addr,uc2_sram_val);    
            }    
        }
    }
   
}


rtk_uint16 alg_tune_giga_6818B_220617_patch[][2]=
{
    {0x80b5 ,0x95} ,
        {0x80b6 ,0xcb},
        {0x80b7 ,0xf6},
        {0x80b8, 0x04},
        {0x80b9 ,0xd2},
        {0x80ba, 0x06} ,
        {0x80bb ,0xf7},
        {0x80bc ,0xbc},
        {0x80bd ,0x4b},
        {0x80be ,0x19} ,
        {0x80bf ,0x2f}, 
        
        {0x80c9, 0xa0},
        {0x80ca ,0xcb},
        {0x80cb ,0xf6},
        {0x80cc ,0x04},
        {0x80cd ,0x9e},
        {0x80ce ,0x06} ,
        {0x80cf ,0xf5} ,
        {0x80d0 ,0xc4},
        {0x80d1 ,0x4c} ,
        {0x80d2 ,0x19},
        {0x80d3 ,0x2f} ,
        
        {0x80c0 ,0x0c},
        {0x80d4 ,0x0c} 
};
void alg_tune_giga_6818B_220617(rtk_uint32 phymask)
{
    rtk_uint32 port,i,uc1_sram_addr,uc1_sram_val,len;

    len= sizeof(alg_tune_giga_6818B_220617_patch)/4;

    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            for(i=0;i<len;i++)
            {
                uc1_sram_addr=alg_tune_giga_6818B_220617_patch[i][0];
                uc1_sram_val=alg_tune_giga_6818B_220617_patch[i][1];        
                uc1_sram_write_8b(port,uc1_sram_addr,uc1_sram_val);    
                         //   OSAL_PRINTF("\naddr %x  data %x",patch_list[i][0],patch_list[i][1]);                     
            }    
            //setPhyMaskRegBits(1<<port,31,0xa87e,12,8,0x6);
            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xa87e, 0x1f<<8, 0x6);
        }
    }
}


void afe_patch_6818B_220607(rtk_uint32 phymask)
{
 //   #cen port 在baseaddr+1 port: e.x. p1/p5
 //   #adjust LDO to improve TM2 jitter
    rtk_uint32 port,i;
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xbf84, 0x7<<0, 0x4);
            dal_rtl8373_phy_regbits_write(1 << port, 31, 0xbf8c, 0x1f<<6, 0x0);
            
            //setPhyMaskRegBits(1<<port,31,0xbf84,2,0,4);    
            //setPhyMaskRegBits(1<<port,31,0xbf8c,10,6,0);    
        }
    }

}






rtk_api_ret_t serdes_patch (rtk_uint32 CHIP_MODE, rtk_uint32 SDS_INDX ,rtk_uint32 SDS_MODE)
{
    rtk_uint16 dig_patch[6][3]={0};
    rtk_uint16 an_patch[17][3]={0};
    rtk_uint16 dig_patch_len,an_patch_len,i;
    switch(SDS_MODE)
    {
        case SERDES_10GUSXG: //usxg
        case SERDES_10GQXG:
        case SERDES_10GR: //usxg

            an_patch_len=sizeof(an_10p3125g);

            memcpy(an_patch,an_10p3125g,an_patch_len);

            if ((CHIP_MODE==CHIP_RTL8224_MODE)&& ((SDS_MODE==SERDES_10GUSXG)||(SDS_MODE==SERDES_10GQXG)))
            {
                dig_patch_len=sizeof(dig_patch_phy);
                memcpy(dig_patch,dig_patch_phy,dig_patch_len);
            }
            else 
            {
                dig_patch_len=sizeof(dig_patch_mac);
                memcpy(dig_patch,dig_patch_mac,dig_patch_len);
            }
            break;

        case SERDES_HSG: //usxg
            an_patch_len=sizeof(an_3p125g);
            memcpy(an_patch,an_3p125g,an_patch_len);
            if (CHIP_MODE==CHIP_RTL8224_MODE)
            {
                dig_patch_len=sizeof(dig_patch_phy);
                memcpy(dig_patch,dig_patch_phy,dig_patch_len);
                
            }
            else 
            {
                dig_patch_len=sizeof(dig_patch_mac);
                memcpy(dig_patch,dig_patch_mac,dig_patch_len);
            }
            break;
        
        case SERDES_SG: //usxg
            an_patch_len=sizeof(an_1p25g);
            memcpy(an_patch,an_1p25g,an_patch_len);
            
            if (CHIP_MODE==CHIP_RTL8224_MODE) 
            {
                dig_patch_len=sizeof(dig_patch_phy);
                memcpy(dig_patch,dig_patch_phy,dig_patch_len);
            }
            else 
            {
                dig_patch_len=sizeof(dig_patch_mac);
                memcpy(dig_patch,dig_patch_mac,dig_patch_len);
            }
        break;
        default :     
            return RT_ERR_INPUT;
            break;
        }

    switch(CHIP_MODE)
    {
        case CHIP_RTL8372_MODE :
        case CHIP_RTL8373_MODE :
            for(i=0;i<an_patch_len/6;i++)
            {
                dal_rtl8373_sds_reg_write(SDS_INDX,an_patch[i][0],an_patch[i][1],an_patch[i][2]);
            }
            for(i=0;i<dig_patch_len/6;i++)
            {
                dal_rtl8373_sds_reg_write(SDS_INDX,dig_patch[i][0],dig_patch[i][1],dig_patch[i][2]);
            }
            break;
        case CHIP_RTL8224_MODE :
            for(i=0;i<an_patch_len/6;i++)
            {
                dal_rtl8224_sds_reg_write(SDS_INDX,an_patch[i][0],an_patch[i][1],an_patch[i][2]);
            }
            for(i=0;i<dig_patch_len/6;i++)
            {
                dal_rtl8224_sds_reg_write(SDS_INDX,dig_patch[i][0],dig_patch[i][1],dig_patch[i][2]);
            }
            break;
        default :     
            return RT_ERR_OK;
            break;
    }

    return RT_ERR_OK;
}

/*
void fw_reset_flow_tgr_8224(rtk_uint32 sdsid)
{
    rtk_uint32 REG_31_21,RXIDLE,NSQ,SYNC_OK,REG_5_0,LINK_OK,HI_BER;
    ret_t retVal;

    //REG_31_21=readsdsreg_8224_via_8373(0,sds,0x1F,0x15);
    retVal = dal_rtl8224_sds_reg_read(sdsid, 0x1F, 0x15, &REG_31_21);
    if(retVal != RT_ERR_OK)
        return retVal;
    RXIDLE=((REG_31_21>>7)&1);
    NSQ=((REG_31_21>>6)&1);

//#切debug port 看SIG_OK
    writesdsreg_8224_via_8373_setbits(0,sds,0x21,0,5,5,1);//#RX_Test_EN
    writesdsreg_8224_via_8373_setbits(0,sds,0x21,0x1b,10,7,9);//#reg0_debug_sel
    writesdsreg_8224_via_8373(0,sds,0x1f,2,0x4A);//#切debug port 

    
 if(NSQ==1 || RXIDLE==0)
 { 
    //#NSQ=1或RXIDLE=0后，若无SYNC_OK则 Rx reset
    REG_5_0=readsdsreg_8224_via_8373(0,sds,0x5,0);
    SYNC_OK=(REG_5_0&1);
    if(SYNC_OK==0)
    {
        //puts "NSQ=1或RXIDLE=0后，若无SYNC_OK则 Rx reset!"
        writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
        writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
        writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
    }
    else
    {
        LINK_OK = ((REG_5_0>>12)&1);
        HI_BER = ((REG_5_0>>1)&1);
        // puts "LINK_OK = $LINK_OK, HI_BER = $HI_BER;"
        if((LINK_OK==0) || (HI_BER==1))
            {
               writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
               writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
               writesdsreg_8224_via_8373_setbits(0,sds,0x20,0,5,4,0x3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            }
     }
  }
}

*/

rtk_api_ret_t fw_reset_flow_tgr_8224(rtk_uint32 sdsid)
{
    rtk_uint32 REG_31_21,RXIDLE,NSQ,SYNC_OK,REG_5_0,LINK_OK,HI_BER,test;
    ret_t retVal;

//#切debug port 看SIG_OK
    /*rtl8371b_sds_reg_setbits(sds,0x21,0,5,5,1);*/    //#RX_Test_EN
    /*rtl8371b_sds_reg_setbits(sds,0x21,0x1b,10,7,9);*/         //#reg0_debug_sel
    /*rtl8371b_sds_reg_set(sds,0x1f,2,0x4A);*/          //#切debug port 

    retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x21, 0, (1<<2), 1);//#RX_Test_EN
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x36, 0x05, (0xf<<11), 8);//##reg0_debug_sel
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = dal_rtl8224_sds_reg_write(sdsid, 0x1f, 0x2, 0x1f);//切debug port 
    if(retVal != RT_ERR_OK)
        return retVal;

    /*REG_31_21=rtl8371b_sds_reg_get(sds,0x1F,0x15);*/
    retVal = dal_rtl8224_sds_reg_read(sdsid, 0x1f, 0x15, &REG_31_21);
    if(retVal != RT_ERR_OK)
        return retVal;
    
    RXIDLE = ((REG_31_21 >> 7)&1);
    NSQ = ((REG_31_21 >> 6)&1);
    if(NSQ==1 || RXIDLE==0)
    { 
    //#NSQ=1或RXIDLE=0后，若无SYNC_OK则 Rx reset
        /*REG_5_0=rtl8371b_sds_reg_get(sds,0x5,0);*/
        retVal = dal_rtl8224_sds_reg_read(sdsid, 0x5, 0x0, &REG_5_0);
        if(retVal != RT_ERR_OK)
            return retVal;
    
        SYNC_OK=(REG_5_0&1);
        if(SYNC_OK==0)
        {

            retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 
    
            retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 

            retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 

            retVal = dal_rtl8224_sds_reg_read(sdsid, 0x5, 0, &test);
            if(retVal != RT_ERR_OK)
                return retVal;
        
        }
        else
        {
            /*REG_5_0=rtl8371b_sds_reg_get(sds,0x5,0);*/

            retVal = dal_rtl8224_sds_reg_read(sdsid, 0x5, 0, &REG_5_0);
            if(retVal != RT_ERR_OK)
                return retVal;
            
            LINK_OK = ((REG_5_0>>12)&1);
            HI_BER = ((REG_5_0>>1)&1);
            // puts "LINK_OK = $LINK_OK, HI_BER = $HI_BER;"
            if((LINK_OK==0) || (HI_BER==1))
            {

                retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal; 
        
                retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal; 

                retVal = dal_rtl8224_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal;
            }
        }
    }
}


rtk_api_ret_t fw_reset_flow_tgr(rtk_uint32 sdsid)
{
    rtk_uint32 REG_31_21,RXIDLE,NSQ,SYNC_OK,REG_5_0,LINK_OK,HI_BER,test;
    ret_t retVal;


    retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x21, 0, (1<<2), 1);//#RX_Test_EN
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x36, 0x5, (0xf<<11), 8);//##reg0_debug_sel
    if(retVal != RT_ERR_OK)
        return retVal;

    retVal = dal_rtl8373_sds_reg_write(sdsid, 0x1f, 0x2, 0x1f);//切debug port 
    if(retVal != RT_ERR_OK)
        return retVal;

    /*REG_31_21=rtl8371b_sds_reg_get(sds,0x1F,0x15);*/
    retVal = dal_rtl8373_sds_reg_read(sdsid, 0x1f, 0x15, &REG_31_21);
    if(retVal != RT_ERR_OK)
        return retVal;
    
    //RXIDLE=(REG_31_21&(1<<7));
    //NSQ=(REG_31_21&(1<<6));
    RXIDLE = ((REG_31_21 >> 7)&1);
    NSQ = ((REG_31_21 >> 6)&1);
    if(NSQ==1 || RXIDLE==0)
    { 
    //#NSQ=1或RXIDLE=0后，若无SYNC_OK则 Rx reset
        /*REG_5_0=rtl8371b_sds_reg_get(sds,0x5,0);*/
        retVal = dal_rtl8373_sds_reg_read(sdsid, 0x5, 0x0, &REG_5_0);
        if(retVal != RT_ERR_OK)
            return retVal;
    
        SYNC_OK=(REG_5_0&1);
        if(SYNC_OK==0)
        {

            retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 
    
            retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 

            retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
            if(retVal != RT_ERR_OK)
                return retVal; 

            retVal = dal_rtl8373_sds_reg_read(sdsid, 0x5, 0, &test);
            if(retVal != RT_ERR_OK)
                return retVal;
        
        }
        else
        {
            /*REG_5_0=rtl8371b_sds_reg_get(sds,0x5,0);*/

            retVal = dal_rtl8373_sds_reg_read(sdsid, 0x5, 0, &REG_5_0);
            if(retVal != RT_ERR_OK)
                return retVal;
            
            LINK_OK = ((REG_5_0>>12)&1);
            HI_BER = ((REG_5_0>>1)&1);
            // puts "LINK_OK = $LINK_OK, HI_BER = $HI_BER;"
            if((LINK_OK==0) || (HI_BER==1))
            {
                /*rtl8371b_sds_reg_setbits(sds,0x20,0,5,4,0x3);*/   //FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                /*rtl8371b_sds_reg_setbits(sds,0x20,0,5,4,0x1);*/   //FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                /*rtl8371b_sds_reg_setbits(sds,0x20,0,5,4,0x3); */  //FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]

                retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal; 
        
                retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 1);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal; 

                retVal = dal_rtl8373_sds_regbits_write(sdsid, 0x20, 0, (0x3<<4), 3);//FRC_RX_EN_VAL[5] FRC_RX_EN_ON[4]
                if(retVal != RT_ERR_OK)
                    return retVal;
            }
        }
    }
}


void afe_patch_6818_220325()
{
    if(CHIP_TYPE == CHIP_RTL8373_MODE )
    {
        //setPhyMaskRegBits(1<<1|1<<5,31,0xbf84,2,0,7);
        //setPhyMaskRegBits(1<<1|1<<5,31,0xbf8c,10,6,0);
        dal_rtl8373_phy_regbits_write(1<<1|1<<5, 31, 0xbf84, 0x7, 7);
        dal_rtl8373_phy_regbits_write(1<<1|1<<5, 31, 0xbf8c, 0x1f<<6, 0);
    }
    else if(CHIP_TYPE == CHIP_RTL8372_MODE )
    {
        //setPhyMaskRegBits(1<<5,31,0xbf84,2,0,7);
        //setPhyMaskRegBits(1<<5,31,0xbf8c,10,6,0);
        dal_rtl8373_phy_regbits_write(1<<5, 31, 0xbf84, 0x7, 7);
        dal_rtl8373_phy_regbits_write(1<<5, 31, 0xbf8c, 0x1f<<6, 0);
    }
}


void alg_tune_fnet_6818_220414(rtk_uint32 phymask)
{
    rtk_uint16 port,i,data_ram_addr,data_ram_val,len;

    len = sizeof(alg_tune_fnet_6818_220414_patch)/4;
//OSAL_PRINTF("\n alg_tune_fnet_6818_220414_patch len  %x",len);
    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            for(i=0;i<len;i++)
            {
                data_ram_addr=alg_tune_fnet_6818_220414_patch[i][0];
                data_ram_val=alg_tune_fnet_6818_220414_patch[i][1];        
                uc1_sram_write_8b(port,data_ram_addr,data_ram_val);    
            }
            
        }
    }
}



void alg_tune_giga_220411(rtk_uint16 phymask)
{
    rtk_uint16 port,len,i,data_ram_addr,data_ram_val;
    
    len = sizeof(alg_tune_giga_220411_patch);

    for(port=0;port<8;port++)
    {
        if((1<<port)&phymask)
        {
            for(i=0;i<len/4;i++)
            {
                data_ram_addr=alg_tune_giga_220411_patch[i][0];
                data_ram_val=alg_tune_giga_220411_patch[i][1];

                uc1_sram_write_8b(port,data_ram_addr,data_ram_val);
            }
        }
    }
}


void data_ram_patch_6818_220325(rtk_uint32 phymask)
{
    rtk_uint16 port,i,len,data_ram_addr,data_ram_val;
    len=sizeof(patch_list)/4;
    for(port=0;port<8;port++)
        {
            if((1<<port)&phymask)
            {
                //setPhyMaskRegBits(1<<port,31,0xb896,0,0,0);
                //setPhyMaskRegBits(1<<port,31,0xb892,15,8,0);

                dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb896, 1<<0, 0);
                dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb892, 0xff<<8, 0);
                for(i=0;i<len;i++)
                {
                    data_ram_addr=patch_list[i][0];
                    data_ram_val=patch_list[i][1];        
                    data_ram_write_8b(port,data_ram_addr,data_ram_val);    
                }
                //setPhyMaskRegBits(1<<port,31,0xb896,0,0,1);
                dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb896, 1<<0, 1);
             }
          
        }
    
}

void pwr_on_patch_phy_v006_rls_lockmain(rtk_uint32 phymask)
{
    rtk_uint32 port,pcs_state,counter,tmp;
    for(port=0;port<8;port++)
    {
        tmp=(1<<port)&phymask;
        if(tmp==0)
            continue;
        //setPhyMaskRegBits(1<<port ,31,0xa4a0 ,10,10,0); 
        dal_rtl8373_phy_regbits_write(1<<port, 31 , 0xa4a0, 1<<10, 0);
        counter=3000;
        do
        {
            //pcs_state=getphyRegBits(port,31,0xa600,7,0);
            dal_rtl8373_phy_regbits_read(port, 31, 0xa600, 0xff, &pcs_state);
            counter--;
        }while(pcs_state==1||counter==0);
        //setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0x801E); 
        //setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,currentVersion); 

        dal_rtl8373_phy_regbits_write(1<<port, 31 , 0xa436, 0xffff, 0x801E);
        dal_rtl8373_phy_regbits_write(1<<port, 31 , 0xa438, 0xffff, currentVersion);
    }
}


void pwr_on_patch_phy_v006(rtk_uint32 phymask)
{
    rtk_uint32 port,fnet_patch_en,giga_patch_en,xg_patch_en,patch_key_addr,patch_key;
    rtk_uint32 patch_rdy,counter,pcs_state;
    rtk_uint32 sel_patch_nc0,sel_patch_nc1,sel_patch_nc2,sel_patch_uc,sel_patch_uc2;
    rtk_uint32 tmp, regdata;
    currentVersion=6;
    
    for(port=0;port<8;port++)
    {
        tmp=(1<<port)&phymask;
        if(tmp==0)
            continue;
        
        /*setPhyMaskReg(1<<port ,31,0xa436 ,DISABLE,0x801E); */

        dal_rtl8373_phy_write(1 << port, 31, 0xa436, 0x801e);
  
        /*FWVersion=getPhyReg(port,31,0xa438);*/

        dal_rtl8373_phy_read(port, 31, 0xa438, &regdata);
        FWVersion = regdata;
        if(FWVersion==currentVersion)
            continue;
  
        fnet_patch_en=1;
        giga_patch_en=1;
        xg_patch_en = 1;

        patch_key_addr=0x8023;
        patch_key=0x1800;

        sel_patch_nc0=xg_patch_en;
        sel_patch_nc1=xg_patch_en;
        sel_patch_nc2=xg_patch_en;
        sel_patch_uc=xg_patch_en;
        sel_patch_uc2=xg_patch_en;

        if(sel_patch_nc0|sel_patch_nc1|sel_patch_nc2|sel_patch_uc|sel_patch_uc2)
        {

            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,4,4,1);*/ 
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<4, 1);
            
            counter=3000;
             
            do
            {
                /*patch_rdy=getphyRegBits(port,31,0xb800,6,6);*/
                dal_rtl8373_phy_regbits_read(port, 31, 0xb800, 1<<6, &patch_rdy);
                delay_loop(10);
                counter--;
            }while(patch_rdy!=1||counter==0);
 
 
            // # Set patch_key & patch_lock
            /*setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,patch_key_addr); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,patch_key); 
            setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0xb82e); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,1); */

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, patch_key_addr);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, patch_key);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, 0xb82e);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 1);
 


            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,7,7,1);*/ 

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<7, 1);

            /*# if you can't do partial write, it is recommended to set b82_16 to be 0x0090
            # where b82_16[4:4] is patch request, b82_16[7:7] is disable dbg_s auto increment,*/
            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,7,7,0); */

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<7, 0);
//# ----------------------------- data_ram_patch START--------------------------------
            data_ram_patch_6818_220325(1<<port);

   //  # Clear patch_key & patch_lock
            /*setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,0); 
            setPhyMaskRegBits(1<<port ,31,0xb82e ,0,0,0); 
            setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,patch_key_addr); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,0); */

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, 0);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 0);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb82e, 1, 0);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, patch_key_addr);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 0);

//# Release patch request & wait patch_rdy = 0
            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,4,4,0); */
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<4, 0);

            counter=3000;
            do
            {
                delay_loop(10);
                /*patch_rdy=getphyRegBits(port,31,0xb800,6,6); */
                dal_rtl8373_phy_regbits_read(port, 31, 0xb800, 1<<6, &patch_rdy);
                counter--;
            }while(patch_rdy!=0||counter==0);

        
                
//## Lock Main
            /*setPhyMaskRegBits(1<<port ,31,0xa4a0 ,10,10,1);*/
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa4a0, 1<<10, 1);

            counter=3000;
            do
             {
                  delay_loop(10);
                  /*pcs_state=getphyRegBits(port,31,0xa600,7,0);*/
                  dal_rtl8373_phy_regbits_read(port, 31, 0xa600, 0xff, &pcs_state);
                 counter--;
            }while(pcs_state!=1||counter==0);
            
 
  
            if(fnet_patch_en || giga_patch_en)
            {
                alg_tune_giga_220411(1<<port);
                alg_tune_fnet_6818_220414(1<<port);
            }

            uc2_sram_write_8b(port ,0x8012,0xee);

            afe_patch_6818_220325();
         
                /*setPhyMaskReg(1<<port ,31,0xA5D0 ,DISABLE,0); 
                setPhyMaskRegBits(1<<port ,31,0xa430 ,2,0,0); 
                setPhyMaskRegBits(1<<port ,31,0xa47e ,7,6,1); 
                setPhyMaskReg(1<<port ,31,0xa610 ,DISABLE,0x2058); */

            dal_rtl8373_phy_write(1<<port, 31, 0xa5d0, 0);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa430, 0x7, 0);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa47e, 3<<6, 1);
            dal_rtl8373_phy_write(1<<port, 31, 0xa610, 0x2058);
    
        }

         
    }
}


void RL6818B_pwr_on_patch_phy_v002_rls_lockmain(rtk_uint32 phymask)
{
    rtk_uint32 port,pcs_state,counter,tmp;
    for(port=0;port<8;port++)
    {
        tmp=(1<<port)&phymask;
        if(tmp==0)
            continue;
        //setPhyMaskRegBits(1<<port ,31,0xa4a0 ,10,10,0); 
        //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa4a0, 1<<10, 0);
        counter=3000;
        do
        {
            //pcs_state=getphyRegBits(port,31,0xa600,7,0);
            dal_rtl8373_phy_regbits_read(port, 31, 0xa600, 0xff, &pcs_state);
            counter--;
        }while(pcs_state==1||counter==0);
               //setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0x801E); 
               //setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,currentVersion); 
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, 0x801e);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, currentVersion);
    }
}


void RL6818B_pwr_on_patch_phy_v002(rtk_uint32 phymask)
{
    rtk_uint32 port,fnet_patch_en,giga_patch_en,xg_patch_en,patch_key_addr,patch_key;
    rtk_uint32 patch_rdy,counter,pcs_state;
    rtk_uint32 sel_patch_nc0,sel_patch_nc1,sel_patch_nc2,sel_patch_uc,sel_patch_uc2;
    rtk_uint32 tmp, regdata;
    currentVersion=6;
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    for(port=0;port<8;port++)
    {
        tmp=(1<<port)&phymask;
        if(tmp==0)
            continue;
        //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
        /*setPhyMaskReg(1<<port ,31,0xa436 ,DISABLE,0x801E); */

        dal_rtl8373_phy_write(1 << port, 31, 0xa436, 0x801e);
  
        /*FWVersion=getPhyReg(port,31,0xa438);*/

        dal_rtl8373_phy_read(port, 31, 0xa438, &regdata);
        FWVersion = regdata;
        if(FWVersion==currentVersion)
            continue;
        //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
        fnet_patch_en=1;
        giga_patch_en=1;
        xg_patch_en = 1;

        patch_key_addr=0x8023;
        patch_key=0x1801;

        sel_patch_nc0=xg_patch_en;
        sel_patch_nc1=xg_patch_en;
        sel_patch_nc2=xg_patch_en;
        sel_patch_uc=xg_patch_en;
        sel_patch_uc2=xg_patch_en;

        if(sel_patch_nc0|sel_patch_nc1|sel_patch_nc2|sel_patch_uc|sel_patch_uc2)
        {

            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,4,4,1);*/ 
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<4, 1);
            
            counter=3000;
             
            do
            {
                /*patch_rdy=getphyRegBits(port,31,0xb800,6,6);*/
                dal_rtl8373_phy_regbits_read(port, 31, 0xb800, 1<<6, &patch_rdy);
                delay_loop(10);
                counter--;
            }while(patch_rdy!=1||counter==0);
            //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
 
            // # Set patch_key & patch_lock
            /*setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,patch_key_addr); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,patch_key); 
            setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0xb82e); 
            setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,1); */

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, patch_key_addr);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, patch_key);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, 0xb82e);
            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 1);
 


            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,7,7,1);*/ 

            dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<7, 1);

            
            if (sel_patch_nc0)
            {
                rst_smtr_patch_6818B_220609(1<<port) ; 
            }
            if (sel_patch_nc1)
            {
               
            }
             if (sel_patch_nc2)
            {
               n2_tp3_patch_6818B_220610(1<<port);
            }
             if (sel_patch_uc2)
            {
               uc2_patch_6818B_220614(1<<port);
            }
          
        }

            /*# if you can't do partial write, it is recommended to set b82_16 to be 0x0090
            # where b82_16[4:4] is patch request, b82_16[7:7] is disable dbg_s auto increment,*/
            /*setPhyMaskRegBits(1<<port ,31,0xb820 ,7,7,0); */

        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<7, 0);
//# ----------------------------- data_ram_patch START--------------------------------
        data_ram_patch_6818B_220616(1<<port);


//  # Clear patch_key & patch_lock
        /*setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,0); 
     setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,0); 
     setPhyMaskRegBits(1<<port ,31,0xb82e ,0,0,0); 
     setPhyMaskRegBits(1<<port ,31,0xa436 ,15,0,patch_key_addr); 
     setPhyMaskRegBits(1<<port ,31,0xa438 ,15,0,0); */

        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, 0);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 0);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb82e, 1, 0);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa436, 0xffff, patch_key_addr);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa438, 0xffff, 0);

//# Release patch request & wait patch_rdy = 0
        /*setPhyMaskRegBits(1<<port ,31,0xb820 ,4,4,0); */
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xb820, 1<<4, 0);

        counter=3000;
        do
        {
            delay_loop(10);
            /*patch_rdy=getphyRegBits(port,31,0xb800,6,6); */
            dal_rtl8373_phy_regbits_read(port, 31, 0xb800, 1<<6, &patch_rdy);
            counter--;
        }while(patch_rdy!=0||counter==0);

    
            
//## Lock Main
        /*setPhyMaskRegBits(1<<port ,31,0xa4a0 ,10,10,1);*/
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa4a0, 1<<10, 1);

        counter=3000;
        do
         {
              delay_loop(10);
              /*pcs_state=getphyRegBits(port,31,0xa600,7,0);*/
              dal_rtl8373_phy_regbits_read(port, 31, 0xa600, 0xff, &pcs_state);
             counter--;
        }while(pcs_state!=1||counter==0);
        //("%s %s %d\n",__FILE__, __func__, __LINE__);

        if(xg_patch_en)
        {
            alg_tune_2p5G_6818B_220616(1<<port);
        }
        if(fnet_patch_en || giga_patch_en)
        {
            alg_tune_giga_6818B_220617(1<<port);
            alg_tune_fnet_6818_220414(1<<port);
        }

        //uc2_sram_write_8b(port ,0x8012,0xee);

        afe_patch_6818B_220607(1<<port);
     
            /*setPhyMaskReg(1<<port ,31,0xA5D0 ,DISABLE,0); 
         setPhyMaskRegBits(1<<port ,31,0xa430 ,2,0,0); 
         setPhyMaskRegBits(1<<port ,31,0xa47e ,7,6,1); 
         setPhyMaskReg(1<<port ,31,0xa610 ,DISABLE,0x2058); */

        dal_rtl8373_phy_write(1<<port, 31, 0xa5d0, 0);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa430, 0x7, 0);
        dal_rtl8373_phy_regbits_write(1<<port, 31, 0xa47e, 3<<6, 1);
        dal_rtl8373_phy_write(1<<port, 31, 0xa610, 0x2058);

    }

     //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
}




void p25gphy_snr_threshold_modify(rtk_uint32 portmask)
{
    rtk_uint32 port,tmp;
    for(port=0;port<8;port++)
    {
        tmp=(1<<port)&portmask;
        if(tmp==0)
        continue;
        uc2_sram_write_8b(port,0x8066,0x35);
        uc2_sram_write_8b(port,0x8067 ,0x0);
        uc2_sram_write_8b(port, 0x8068 ,0x35);
        uc2_sram_write_8b(port,0x8069 ,0x0);
        uc2_sram_write_8b(port, 0x806E,0x02);
        uc2_sram_write_8b(port,0x806F, 0xa0);
    }
}


rtk_api_ret_t rtl8373_8224_init()
{
    rtk_uint32 i;
    rtk_uint32 tmp;

    ret_t retVal;
        
        
    printf("%s %s %d\n",__FILE__, __func__, __LINE__);
      //******************** End to Reset RTL8224 by RTL8373_GPIO36 ***************************
      Pin_Reset_8224_via_8373();
      //******************** Begin to Initial RTL8373 MDC/MDIO ********************************
      //  puts "MDC/MDIO pad initial"
      //setRegBits(RTL8371C_SMI_MAC_TYPE_CTRL_ADDR , 17, 16, 0);  //MAC_PORT8_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
      //setRegBits(RTL8371C_SMI_PORT_POLLING_SEL_ADDR , 7, 0, 0xff);// RTL8373 set port0-8 polling internal resolution reg
      //setRegBits(RTL8371C_SMI_CTRL_ADDR  , 14,12, 7);    //enable SMI0/1/2 MDC clock output, default is 0

    rtl8373_setAsicRegBits(RTL8373_SMI_MAC_TYPE_CTRL_ADDR, RTL8373_SMI_MAC_TYPE_CTRL_MAC_PORT8_TYPE_MASK, 0);//MAC_PORT8_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
    rtl8373_setAsicRegBits(RTL8373_SMI_PORT_POLLING_SEL_ADDR, 0xff, 0xff); // RTL8373 set port0-8 polling internal resolution reg
    rtl8373_setAsicRegBits(RTL8373_SMI_CTRL_ADDR, 0x7000, 7);//enable SMI0/1/2 MDC clock output, default is 0
      //******************** End to Initial RTL8373 MDC/MDIO ********************************
    
    //wdbs_8224_via_8373();
     // wdbs_8224_top_reg_low_half_via_8373(0,0x24,0,0,1);
    //dal_rtl8224_top_regbit_write(RTL8373_RST_GLB_CTRL_0_ADDR, RTL8373_RST_GLB_CTRL_0_SW_CHIP_RST_OFFSET, 1);
    delay_loop(100);

   
      //  puts "Power down PHY 0~7"
     // setPhyMaskReg(0xFF ,31,0xa610 ,DISABLE,0x2858);
      
     
      //******************** Begin to Initial RTL8373+RTL8224 SerDes configuration ***************************
      //  ####################  SerDes initial begin ###################
    //  #解决8373 port0-2 MACLINK 之前需要Sds0 link一次的bug
    
    
        /*setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 14, 10, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    
        setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0xD);//SDS0_MODE_SEL = 0xD
    
        rtl8371b_sds_reg_setbits(0,6,1,2,2,1);//#serdes0 AFE loopback
        delay_loop(20);
        rtl8371b_sds_reg_setbits(0,6,1,2,2,0);//#关闭loopback
    
        setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0x1F);//SDS0_MODE_SEL = 0x1F */
      //serdes_patch(CHIP_RTL8373_MODE,0,SERDES_10GQXG),
      /*setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 14, 10, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    
        setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0xD);//SDS0_MODE_SEL = 0xD */

    rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD
    dal_rtl8373_sds_regbits_write(0, 6, 1, 0x4, 1);
    delay_loop(20);
    dal_rtl8373_sds_regbits_write(0, 6, 1, 0x4, 0);

    rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1F);//SDS0_MODE_SEL = 0x1F
    serdes_patch(CHIP_RTL8373_MODE,0,SERDES_10GQXG),
    rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    rtl8373_setAsicRegBits(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD
   
    
      //  #RTL8224 SerDes patch 
      //wdbs_8224_top_reg_low_half_via_8373(0,RTL8371C_SDS_MODE_SEL_ADDR,4,0,0x1F);
      //wdbs_8224_top_reg_low_half_via_8373(0,RTL8371C_SDS_MODE_SEL_ADDR   , 14, 10, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    //wdbs_8224_top_reg_low_half_via_8373(0,RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0xD);//SDS0_MODE_SEL = 0xD
     //wdbs_8224_top_reg_low_half_via_8373(0,RTL8371C_CFG_PHY_MISC_ADDR  ,9,9,1); // #RTL8224 SDS0 ????????????
    dal_rtl8224_top_regbits_write(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0x1f);
    serdes_patch(CHIP_RTL8224_MODE,0,SERDES_10GQXG);
    dal_rtl8224_top_regbits_write(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_USX_SUB_MODE_MASK, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
    dal_rtl8224_top_regbits_write(RTL8373_SDS_MODE_SEL_ADDR, RTL8373_SDS_MODE_SEL_SDS0_MODE_SEL_MASK, 0xD);//SDS0_MODE_SEL = 0xD
    
    //dal_rtl8224_top_regbit_write(RTL8373_CFG_PHY_MISC_ADDR,RTL8373_CFG_PHY_MISC_CFG_BYP_SDS_LDN_OFFSET, 1);
    delay_loop(50);
    //fw_tgr_reset_flow_8224_via_8373(0);
    fw_reset_flow_tgr_8224(0);
#if 0    
    delay_loop(50);
    fw_reset_flow_tgr(1);
#endif     
    delay_loop(50);
    fw_reset_flow_tgr(0);
     // delay_loop(50);
    //  fw_reset_flow_tgr_8224(0);
    printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    //    puts "Power down PHY 0~7" 
      //setPhyMaskReg(0xFF ,31,0xa610 ,DISABLE,0x2858);
      /*setRegBits(RTL8371C_CFG_PHY_MDI_REVERSE_ADDR,3,0,0xc);
      wdbs_8224_top_reg_low_half_via_8373(0,RTL8371C_CFG_PHY_MDI_REVERSE_ADDR,3,0,0xc);
      setReg(0x5ff0,0);
      wd_8224_top_reg_low_half_via_8373(0,0x5ff0,0);
    setPhyMaskReg(0xFF ,31,0xa610 ,DISABLE,0x2858); */

    rtl8373_setAsicRegBits(RTL8373_CFG_PHY_MDI_REVERSE_ADDR, 0xf, 0xc);
    dal_rtl8224_top_regbits_write(RTL8373_CFG_PHY_MDI_REVERSE_ADDR, 0xf, 0xc);
    rtl8373_setAsicReg(0x5ff0, 0);
    dal_rtl8224_top_reg_write(0x5ff0, 0);
    dal_rtl8373_phy_write(0xff, 31, 0xa610, 0x2858);
    
    
      //## ---------------------------Patch MAC--------------------------
    // #set MAC_L2_GLOBAL_CTRL0 0x5FD4
      //setRegBits(RTL8371C_MAC_L2_GLOBAL_CTRL0_ADDR,20,20,1);
      //setRegBits(RTL8371C_MAC_L2_GLOBAL_CTRL0_ADDR,19,19,1);

    rtl8373_setAsicRegBit(RTL8373_MAC_L2_GLOBAL_CTRL0_ADDR,RTL8373_MAC_L2_GLOBAL_CTRL0_FWD_INVLD_MAC_CTRL_EN_OFFSET,1);
    rtl8373_setAsicRegBit(RTL8373_MAC_L2_GLOBAL_CTRL0_ADDR,RTL8373_MAC_L2_GLOBAL_CTRL0_FWD_UNKN_OPCODE_EN_OFFSET,1);
    
    printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    //  #BYP_TX_CRC=1
    for(i=0;i<9;i++)
    {
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),2,2,1);  //#BYP_TX_CRC=1, pkt_Gen 时需 dis, 即赋值为0
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),4,4,1); //#RX_CHK_CRC_EN=1
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),8,8,1); //#CLOCK_SWITCH=1; 为解决某些linkdown时因clock停掉而无法drain out的问题

        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_BYP_TX_CRC_OFFSET,1);
        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_RX_CHK_CRC_EN_OFFSET,1);
        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_CLOCK_SWITCH_OFFSET,1);
    }
    printf("%s %s %d\n",__FILE__, __func__, __LINE__);
        //setRegBits(RTL8371C_RS_LAYER_CONFIG_ADDR,5,5,1); //#by华维 RS_LINK_FAULT_INDI_OFF=1 disable link fault flag
                                                                       // #解决port4-7 linkdown DSC累积问题
    rtl8373_setAsicRegBit(RTL8373_RS_LAYER_CONFIG_ADDR,RTL8373_RS_LAYER_CONFIG_RS_LINK_FAULT_INDI_OFF_OFFSET,1);
    
    //## ---------------------------Init END--------------------------       
    
    //setRegBits(RTL8371C_DW8051_CFG_ADDR,RTL8371C_DW8051_CFG_DW8051_READY_OFFSET,0,ENABLE);
    rtl8373_setAsicRegBit(RTL8373_DW8051_CFG_ADDR,RTL8373_DW8051_CFG_DW8051_READY_OFFSET,ENABLE);
    
    delay_loop(50);                                                              
    //setPhyMaskReg(0xff ,31,0xa610 ,DISABLE,0x2058);
#if PHY_PATCH
    // test_patch_phy_rl6818(0xff);
    RL6818B_pwr_on_patch_phy_v002(0xff);
    RL6818B_pwr_on_patch_phy_v002_rls_lockmain(0xff);
#endif
    printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    //p25gphy_snr_threshold_modify(0xff);
    
    //setPhyMaskReg(0xff ,31,0xa610 ,DISABLE,0x2058); 
    //enable polling for RTL8373_RTL8224 Demo
    //setRegBits(RTL8371C_SMI_GLB_CTRL_ADDR , 20, 12,0x1ff);//RTL8373 set polling mask 0x1ff, port 8 from serdes need config bit8=1

    dal_rtl8373_phy_write(0xff, 31, 0xa610, 0x2058);
    rtl8373_setAsicRegBits(RTL8373_SMI_GLB_CTRL_ADDR,RTL8373_SMI_GLB_CTRL_SMI_POLLING_MASK_MASK,0x1ff);
    
}



rtk_api_ret_t rtl8372_init()
{
    rtk_uint32 i,ret;

  //******************** Begin to Initial RTL8373 MDC/MDIO ********************************
  //  puts "MDC/MDIO pad initial"
  /*setRegBits(RTL8371C_SMI_MAC_TYPE_CTRL_ADDR , 17, 16, 0);  //MAC_PORT8_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
  setRegBits(RTL8371C_SMI_MAC_TYPE_CTRL_ADDR , 7, 6, 0);  //MAC_PORT3_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
  setRegBits(RTL8371C_SMI_PORT_POLLING_SEL_ADDR , 7, 4, 0xf);// RTL8373 set port4-7 polling internal resolution reg
  setRegBits(RTL8371C_SMI_CTRL_ADDR  , 14,12, 7);    //enable SMI0/1/2 MDC clock output, default is 0 */
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    rtl8373_setAsicRegBits(RTL8373_SMI_MAC_TYPE_CTRL_ADDR, RTL8373_SMI_MAC_TYPE_CTRL_MAC_PORT8_TYPE_MASK, 0);//MAC_PORT8_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
    rtl8373_setAsicRegBits(RTL8373_SMI_MAC_TYPE_CTRL_ADDR, RTL8373_SMI_MAC_TYPE_CTRL_MAC_PORT3_TYPE_MASK, 0);//MAC_PORT3_TYPE=0 port type: RTL8373 default set port0-7 polling 10G/2.5GPHY
    rtl8373_setAsicRegBits(RTL8373_SMI_PORT_POLLING_SEL_ADDR, 0xf0, 0xf); // RTL8373 set port0-8 polling internal resolution reg
    rtl8373_setAsicRegBits(RTL8373_SMI_CTRL_ADDR, 0x7000, 7);//enable SMI0/1/2 MDC clock output, default is 0
  //******************** End to Initial RTL8373 MDC/MDIO ********************************
    delay_loop(100);

  //******************** Begin to Initial RTL8373+RTL8224 SerDes configuration ***************************
  //  ####################  SerDes initial begin ###################
 // setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 14, 10, 2);//SDS0_USX_SUB_MODE = 0x2, default is 0x2 10G-QXGMII
  /*setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0x1F);//SDS0_MODE_SEL = 0x1F
  setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 9, 5,0x1F);//SDS1_MODE_SEL = 0x1F
  serdes_patch(CHIP_RTL8372,0,SERDES_10GR);
  serdes_patch(CHIP_RTL8372,1,SERDES_10GR);

  setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 4, 0,0x1A);//SDS0_MODE_SEL = 0x1F
  setRegBits(RTL8371C_SDS_MODE_SEL_ADDR   , 9, 5,0x1A);//SDS1_MODE_SEL = 0x1F */

    //   ## tgr reset flow
    delay_loop(50);
    fw_reset_flow_tgr(0);
    delay_loop(50);
    fw_reset_flow_tgr(1);


  //******************** Begin to Initial RTL8373+RTL8224 PHY configuration ***************************

  
    //#MDI reverse configuration for Demo Tap UP RJ45, RTL8372
    //setRegBits(RTL8371C_CFG_PHY_MDI_REVERSE_ADDR, 3, 0,0xc);

    rtl8373_setAsicRegBits(RTL8373_CFG_PHY_MDI_REVERSE_ADDR, 0xf, 0xc);

  //  puts "Power down PHY 4~7"
    //setPhyMaskReg(0xF0 ,31,0xa610 ,DISABLE,0x2858);
    dal_rtl8373_phy_write(0xf0, 31, 0xa610, 0x2858);

//  ## ---------------------------Patch MAC--------------------------

    //setRegBits(RTL8371C_MAC_L2_GLOBAL_CTRL0_ADDR,20,19,3);

    rtl8373_setAsicRegBit(RTL8373_MAC_L2_GLOBAL_CTRL0_ADDR,RTL8373_MAC_L2_GLOBAL_CTRL0_FWD_INVLD_MAC_CTRL_EN_OFFSET,1);
    rtl8373_setAsicRegBit(RTL8373_MAC_L2_GLOBAL_CTRL0_ADDR,RTL8373_MAC_L2_GLOBAL_CTRL0_FWD_UNKN_OPCODE_EN_OFFSET,1);

    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);

  //  #BYP_TX_CRC=1
    for(i=3;i<9;i++)
    {
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),2,2,1);
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),4,4,1);
        //setRegBits(RTL8371C_MAC_L2_PORT_CTRL_ADDR(i),8,8,1);

        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_BYP_TX_CRC_OFFSET,1);
        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_RX_CHK_CRC_EN_OFFSET,1);
        rtl8373_setAsicRegBit(RTL8373_MAC_L2_PORT_CTRL_ADDR(i),RTL8373_MAC_L2_PORT_CTRL_CLOCK_SWITCH_OFFSET,1);
    }

//#by华维 RS_LINK_FAULT_INDI_OFF=1 disable link fault flag
  //                                                                  #解决port4-7 linkdown DSC累积问题
    //setRegBits(RTL8371C_RS_LAYER_CONFIG_ADDR,5,5,1);
    rtl8373_setAsicRegBit(RTL8373_RS_LAYER_CONFIG_ADDR,RTL8373_RS_LAYER_CONFIG_RS_LINK_FAULT_INDI_OFF_OFFSET,1);

//## ---------------------------Init END--------------------------
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);

    //setRegBits(RTL8371C_DW8051_CFG_ADDR,RTL8371C_DW8051_CFG_DW8051_READY_OFFSET,0,ENABLE);
    rtl8373_setAsicRegBit(RTL8373_DW8051_CFG_ADDR,RTL8373_DW8051_CFG_DW8051_READY_OFFSET,ENABLE);

    delay_loop(200);
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
#if PHY_PATCH
    RL6818B_pwr_on_patch_phy_v002(0xf0);
    RL6818B_pwr_on_patch_phy_v002_rls_lockmain(0xf0);
#endif
    //p25gphy_snr_threshold_modify(0xf0);
  //setPhyMaskReg(0xF0 ,31,0xa610 ,DISABLE,0x2058);
  //enable polling for RTL8373_RTL8224 Demo
  //setRegBits(RTL8371C_SMI_GLB_CTRL_ADDR , 20, 12,0x1f8);//RTL8373 set polling mask 0x1ff, port 8 from serdes need config bit8=1
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    dal_rtl8373_phy_write(0xf0, 31, 0xa610, 0x2058);
    rtl8373_setAsicRegBits(RTL8373_SMI_GLB_CTRL_ADDR,RTL8373_SMI_GLB_CTRL_SMI_POLLING_MASK_MASK,0x1f8);

    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
}    



/* Function Name:
 *      dal_rtl8373_switch_init
 * Description:
 *      Set chip to default configuration enviroment
 * Input:
 *      None
 * Output:
 *      None
 * Return:
 *      RT_ERR_OK           - OK
 *      RT_ERR_FAILED       - Failed
 *      RT_ERR_SMI          - SMI access error
 * Note:
 *      The API can set chip registers to default configuration for different release chip model.
 */
rtk_api_ret_t dal_rtl8373_switch_init()
{
    ret_t retVal;
    rtk_uint32 regdata;

    if((retVal = rtl8373_getAsicReg(0x4, &regdata)) != RT_ERR_OK)
        return retVal;
    //printf("%s %s %d\n",__FILE__, __func__, __LINE__);
    regdata = regdata >> 16;
    //printf("%s %s %d 0x%x\n",__FILE__, __func__, __LINE__, regdata);
    if (regdata = 0x8373)
    {
        CHIP_TYPE = CHIP_RTL8373_MODE;
        return rtl8373_8224_init();
    }
    else if (regdata = 0x8372)
    {
        CHIP_TYPE = CHIP_RTL8372_MODE;
        return rtl8372_init();
    }
    else if (regdata = 0x8224)
        CHIP_TYPE = CHIP_RTL8224_MODE;
    else
        return RT_ERR_CHIP_NOT_FOUND;

    return RT_ERR_OK;
}

