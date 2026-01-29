import 'package:flutter/material.dart';

import '../../components/pokemon_display/pokemon_gif_image.dart';
import '../../models/pokemon.model.dart';

class SandboxView extends StatelessWidget {
  const SandboxView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: 400,
        child: Center(
          child: Wrap(
            children: [
              for (int i = 926; i < 958; i++)
                PokemonGifImage(
                  gifUrl: PokemonModel.baseGifUrl(i),
                  height: 50,
                  width: 50,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
