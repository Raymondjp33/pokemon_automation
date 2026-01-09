import 'package:flutter/material.dart';
import 'package:gif/gif.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/catch.model.dart';
import '../../../../models/pokemon.model.dart';

class UnownDisplay extends StatelessWidget {
  const UnownDisplay({required this.pokemon, super.key});

  final List<PokemonModel> pokemon;

  @override
  Widget build(BuildContext context) {
    Map<String, int> catchCounter = {};

    for (CatchModel unown in (pokemon.firstOrNull?.catches ?? [])) {
      List<String> splitList = unown.name?.split(':') ?? [];

      if (splitList.length < 2) {
        continue;
      }
      catchCounter[splitList[1]] = catchCounter[splitList[1]] == null
          ? 1
          : catchCounter[splitList[1]]! + 1;
    }

    return Column(
      children: [
        Expanded(
          child: Column(
            children: [
              for (int i = 0; i < 4; i++)
                Container(
                  height: 58,
                  child: Row(
                    children: [
                      for (int j = 0; j < 7; j++)
                        Container(
                          child: Column(
                            children: [
                              Gif(
                                width: 40,
                                height: 30,
                                image: NetworkImage(
                                  unownGifURL(unownMap[i * 7 + j]),
                                ),
                                fit: BoxFit.contain,
                                autostart: Autostart.loop,
                                useCache: false,
                              ),
                              Text(
                                '${catchCounter[unownMap[i * 7 + j]] ?? 0}',
                                style: AppTextStyles.pokePixel(fontSize: 20),
                              ),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
              Spacer(),
              Row(
                children: [
                  Text(
                    'Total Encounters',
                    style: AppTextStyles.pokePixel(fontSize: 26),
                  ),
                  Spacer(),
                  Text(
                    '${pokemon.firstOrNull?.encounters ?? 0}',
                    style: AppTextStyles.pokePixel(fontSize: 26),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

String unownGifURL(String letter) => letter == 'a'
    ? 'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/200.gif'
    : 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/shiny/201-$letter.gif';

const unownMap = [
  'a',
  'b',
  'c',
  'd',
  'e',
  'f',
  'g',
  'h',
  'i',
  'j',
  'k',
  'l',
  'm',
  'n',
  'o',
  'p',
  'q',
  'r',
  's',
  't',
  'u',
  'v',
  'w',
  'x',
  'y',
  'z',
  'exclamation',
  'question',
];
