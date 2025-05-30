import 'package:flutter/material.dart';
import 'package:gif/gif.dart';

class PokemonGifImage extends StatelessWidget {
  const PokemonGifImage({
    required this.dexNum,
    this.width,
    this.height,
    super.key,
  });

  final String dexNum;
  final double? width;
  final double? height;

  @override
  Widget build(BuildContext context) {
    return Gif(
      width: width,
      height: height,
      image: NetworkImage(
        'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$dexNum.gif',
      ),
      fit: BoxFit.contain,
      autostart: Autostart.loop,
      useCache: false,
    );
  }
}
