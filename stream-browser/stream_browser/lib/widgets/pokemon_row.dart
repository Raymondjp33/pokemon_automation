import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../constants/app_styles.dart';
import '../models/pokemon.model.dart';
import '../models/target.model.dart';
import '../services/file_provider.dart';
import 'pokemon_gif_image.dart';

class PokemonRow extends StatelessWidget {
  const PokemonRow({
    required this.targets,
    this.pokemonGifSize = 100,
    super.key,
  });

  final List<TargetModel> targets;
  final double pokemonGifSize;

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (TargetModel target
            in fileProvider.streamData?.switch2Targets ?? [])
          Builder(
            builder: (context) {
              PokemonModel? pokemonModel =
                  fileProvider.getPokemonModel(target.name);

              if (pokemonModel == null) {
                return Container();
              }

              return Container(
                padding: EdgeInsets.symmetric(horizontal: 10),
                child: Column(
                  children: [
                    PokemonGifImage(
                      width: pokemonGifSize,
                      height: pokemonGifSize,
                      dexNum: target.dexNum,
                    ),
                    Text(
                      '${pokemonModel.totalEncounters}',
                      style: AppTextStyles.pokePixel(fontSize: 40),
                    ),
                    Text(
                      '${pokemonModel.catches?.length ?? 0}/${target.target} ${target.mainTarget ? "(Target)" : ''}',
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
