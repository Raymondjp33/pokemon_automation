import 'package:flutter/material.dart';

import '../../constants/app_styles.dart';
import '../../models/catch.model.dart';
import '../../models/pokemon.model.dart';
import 'pokemon_gif_image.dart';

class UnownDisplay extends StatelessWidget {
  const UnownDisplay({required this.pokemon, super.key});

  final List<PokemonModel> pokemon;

  @override
  Widget build(BuildContext context) {
    Map<String, int> catchCounter = {};
    Set uniqueMap = {};
    int catchEncounterCount = 0;

    for (CatchModel unown in (pokemon.firstOrNull?.catches ?? [])) {
      List<String> splitList = unown.name?.split(':') ?? [];
      catchEncounterCount =
          catchEncounterCount + (unown.encounters?.toInt() ?? 0);
      if (splitList.length < 2) {
        continue;
      }

      String letter = splitList[1];
      catchCounter[letter] =
          catchCounter[letter] == null ? 1 : catchCounter[letter]! + 1;

      uniqueMap.add(letter);
    }

    return Column(
      children: [
        Expanded(
          child: Column(
            children: [
              for (int i = 0; i < 4; i++)
                Container(
                  child: Row(
                    children: [
                      for (int j = 0; j < 7; j++)
                        Container(
                          child: Column(
                            children: [
                              PokemonGifImage(
                                width: 40,
                                height: 29,
                                gifUrl: unownGifURL(unownMap[i * 7 + j]),
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  UnownLineItem(
                    title: 'Total Encs',
                    info: '${pokemon.firstOrNull?.encounters ?? 0}',
                  ),
                  UnownLineItem(
                    title: 'Phases',
                    info: '${pokemon.firstOrNull?.catches?.length ?? 0}',
                  ),
                  UnownLineItem(
                    title: 'Unique',
                    info: '${uniqueMap.length}/28',
                  ),
                  UnownLineItem(
                    title: 'Current',
                    info:
                        '${(pokemon.firstOrNull?.encounters ?? 0) - catchEncounterCount}',
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

class UnownLineItem extends StatelessWidget {
  const UnownLineItem({required this.title, required this.info, super.key});

  final String title;
  final String info;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          title,
          style: AppTextStyles.pokePixel(fontSize: 22),
        ),
        Text(
          info,
          style: AppTextStyles.pokePixel(fontSize: 34),
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
