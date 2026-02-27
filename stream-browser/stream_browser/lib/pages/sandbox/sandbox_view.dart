import 'package:flutter/material.dart';

import '../../components/pokemon_display/pokemon_gif_image.dart';
import '../../models/pokemon.model.dart';

class SandboxView extends StatelessWidget {
  const SandboxView({super.key});

  @override
  Widget build(BuildContext context) {
    // Hisuian
    // int low = 926;
    // int high = 958;

    // Alolan
    // int low = 802;
    // int high = 819;

    // Alolan
    int low = 908;
    int high = 920;

    return Scaffold(
      body: Container(
        width: 600,
        child: Center(
          child: Wrap(
            children: [
              for (int i = low; i < high; i++)
                Column(
                  children: [
                    PokemonGifImage(
                      gifUrl: PokemonModel.baseGifUrl(i),
                      height: 75,
                      width: 75,
                    ),
                    Text(i.toString())
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
