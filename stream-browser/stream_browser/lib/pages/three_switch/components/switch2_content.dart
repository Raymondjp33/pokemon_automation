import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../constants/app_styles.dart';
import '../../../models/pokemon.model.dart';
import '../../../models/target.model.dart';
import '../../../services/file_provider.dart';
import '../../../widgets/pokemon_gif_image.dart';
import '../../../widgets/scrolling_widget.dart';

class Switch2Content extends StatelessWidget {
  const Switch2Content({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();

    return ScrollingWidget(
      scrollSpeed: 30,
      child: Row(
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
                  decoration: BoxDecoration(
                    border: Border.symmetric(
                      vertical: BorderSide(color: Colors.black54),
                    ),
                  ),
                  child: Column(
                    children: [
                      PokemonGifImage(
                        width: 90,
                        height: 90,
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
      ),
    );
  }
}
