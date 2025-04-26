import 'package:flutter/material.dart';

class AppTextStyles {
  static TextStyle pokePixel({double? fontSize}) {
    return TextStyle(
      fontSize: fontSize,
      color: Colors.white,
      height: 1.2,
      fontFamily: 'Pokemon-Pixel',
    );
  }

  // static TextStyle minecraft({double? fontSize}) {
  //   return TextStyle(
  //     fontSize: fontSize,
  //     color: Colors.white,
  //     fontFamily: 'Minecraft',
  //   );
  // }

  static TextStyle minecraftTen({double? fontSize}) {
    return TextStyle(
      fontSize: fontSize,
      color: Colors.white,
      fontFamily: 'Minecraft-Ten',
    );
  }
}
