import 'package:flutter/material.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import 'pokemon_gif_image.dart';

class PokemonRow extends StatelessWidget {
  const PokemonRow({
    required this.targets,
    this.pokemonGifSize = 100,
    this.smallFont = false,
    super.key,
  });

  final List<PokemonModel>? targets;
  final double pokemonGifSize;
  final bool smallFont;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (PokemonModel pokemon in targets ?? [])
          Builder(
            builder: (context) {
              return Container(
                padding: EdgeInsets.symmetric(horizontal: 10),
                child: Column(
                  children: [
                    PokemonGifImage(
                      width: pokemonGifSize,
                      height: pokemonGifSize,
                      dexNum: '${pokemon.pokemonId - 1}',
                    ),
                    Text(
                      '${pokemon.encounters}',
                      style: AppTextStyles.pokePixel(
                        fontSize: smallFont ? 32 : 40,
                      ),
                    ),
                    Text(
                      '${pokemon.catches?.length ?? 0}/${pokemon.targets}',
                      style: AppTextStyles.pokePixel(fontSize: 24),
                    ),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }
}
