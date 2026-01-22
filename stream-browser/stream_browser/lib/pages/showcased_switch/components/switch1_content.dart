import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../constants/app_styles.dart';
import '../../../models/pokemon.model.dart';
import '../../../services/file_provider.dart';
import '../../../widgets/spacing.dart';
import '../../../components/pokemon_display/encounter_timer.dart';

class Switch1Content extends StatelessWidget {
  const Switch1Content({super.key});

  @override
  Widget build(BuildContext context) {
    final PokemonModel? pokemon =
        context.select((FileProvider e) => e.switch1Pokemon.firstOrNull);

    int currentEncounters = pokemon?.encounters ?? 0;
    String shinyCounts =
        '${(pokemon?.catches ?? []).length}/${pokemon?.targets ?? 0}';
    String switch1GifNumber = '${pokemon?.gifNumber ?? 1}';
    int? startTime = pokemon?.startedHuntTimestamp?.toInt();

    return Center(
      child: Row(
        children: [
          Container(
            width: 120,
            height: 108,
            child: Gif(
              image: NetworkImage(
                'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$switch1GifNumber.gif',
              ),
              fit: BoxFit.contain,
              autostart: Autostart.loop,
            ),
          ),
          HorizontalSpace(10),
          Flexible(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(
                  children: [
                    Text(
                      '$currentEncounters',
                      style: AppTextStyles.pokePixel(
                        fontSize: 52,
                      ),
                    ),
                    HorizontalSpace(30),
                    Text(
                      shinyCounts,
                      style: AppTextStyles.pokePixel(
                        fontSize: 32,
                      ),
                    ),
                  ],
                ),
                EncounterTimer(
                  startTime: startTime,
                  endTime: null,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
