import 'package:json_annotation/json_annotation.dart';

import 'catch.model.dart';

part 'pokemon.model.g.dart';

@JsonSerializable(explicitToJson: true)
class PokemonModel {
  String name;
  int targets;
  int switchNum;
  int encounters;
  @JsonKey(name: 'pokemon_id')
  String pokemonId;
  @JsonKey(name: 'total_dens')
  int totalDens;
  @JsonKey(name: 'started_hunt_ts')
  num? startedHuntTimestamp;

  List<CatchModel>? catches;

  PokemonModel({
    this.name = '',
    this.targets = 1,
    this.switchNum = 1,
    this.pokemonId = '1',
    this.encounters = 0,
    this.totalDens = 0,
    this.startedHuntTimestamp,
    this.catches,
  });

  static PokemonModel get emptyPokemon => PokemonModel();

  String get gifUrl {
    int? pokemonIdNum = int.tryParse(pokemonId);
    pokemonIdNum ??= 1;

    if (pokemonId.contains('-') || pokemonIdNum > 1010) {
      return specificGifNumber;
    }

    int gifValue = pokemonIdNum - 1;
    // 802 - 819 Alolan pokemon
    if (pokemonIdNum > 802) {
      gifValue = gifValue + 18;
    }

    // 908 - 920 Galarian pokemon
    if (gifValue > 907) {
      gifValue = gifValue + 13;
    }

    // 926 - 958 Galarian / Hisuian pokemon
    if (gifValue > 925) {
      gifValue = gifValue + 23;
    }

    return baseGifUrl(gifValue);
  }

  String get specificGifNumber {
    switch (pokemonId) {
      // Alolan Meowth
      case '52-1':
        return baseGifUrl(811);
      // Hisuian Sneasel
      case '215-1':
        return baseGifUrl(948);
      // Hisuian Qwilfish
      case '211-1':
        return baseGifUrl(947);
      // Hisuian Basculin (White)
      case '550-1':
        return baseGifUrl(951);
      case '1012':
        return showdownGifUrl(1012);
    }

    return baseGifUrl(1);
  }

  static String baseGifUrl(int num) {
    return 'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$num.gif';
  }

  static String showdownGifUrl(int num) {
    return 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/home/shiny/$num.png';
  }

  factory PokemonModel.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('PokemonModel: json was null');
    try {
      return _$PokemonModelFromJson(json);
    } catch (e, stack) {
      throw 'PokemonModel.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$PokemonModelToJson(this);
    return json;
  }
}
