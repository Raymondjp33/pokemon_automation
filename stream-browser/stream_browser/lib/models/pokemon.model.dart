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
  int pokemonId;
  @JsonKey(name: 'total_dens')
  int totalDens;
  @JsonKey(name: 'started_hunt_ts')
  num? startedHuntTimestamp;

  List<CatchModel>? catches;

  PokemonModel({
    this.name = '',
    this.targets = 1,
    this.switchNum = 1,
    this.pokemonId = 1,
    this.encounters = 0,
    this.totalDens = 0,
    this.startedHuntTimestamp,
    this.catches,
  });

  static PokemonModel get emptyPokemon => PokemonModel();

  int get gifNumber {
    int gifValue = pokemonId - 1;
    if (pokemonId > 802) {
      gifValue = gifValue + 18;
    }

    if (gifValue > 907) {
      gifValue = gifValue + 13;
    }

    return gifValue;
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
