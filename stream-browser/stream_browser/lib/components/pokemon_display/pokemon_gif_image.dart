import 'package:flutter/material.dart';
import 'package:gif/gif.dart';

class PokemonGifImage extends StatelessWidget {
  const PokemonGifImage({
    required this.gifUrl,
    this.width,
    this.height,
    super.key,
  });

  final String gifUrl;
  final double? width;
  final double? height;

  @override
  Widget build(BuildContext context) {
    return Gif(
      width: width,
      height: height,
      image: NetworkImage(
        gifUrl,
      ),
      fit: BoxFit.contain,
      autostart: Autostart.loop,
      useCache: false,
    );
  }
}
