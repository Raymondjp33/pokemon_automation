import 'package:json_annotation/json_annotation.dart';

import 'catch.model.dart';

part 'pokemon.model.g.dart';

@JsonSerializable(explicitToJson: true)
class PokemonData {
  String? pokemon;
  @JsonKey(name: 'encounter_method')
  String? encounterMethod;
  int? encounters;
  @JsonKey(name: 'extra_data')
  Map<String, dynamic>? extraData;
  @JsonKey(name: 'caught_timestamp')
  num? caughtTimestamp;
  @JsonKey(name: 'started_hunt_timestamp')
  num? startedHuntTimestamp;

  List<CatchModel>? catches;

  PokemonData({
    this.pokemon,
    this.encounters,
    this.encounterMethod,
    this.extraData,
    this.caughtTimestamp,
    this.startedHuntTimestamp,
    this.catches,
  });

  static PokemonData get emptyPokemon => PokemonData();

  factory PokemonData.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('PokemonData: json was null');
    try {
      return _$PokemonDataFromJson(json);
    } catch (e, stack) {
      throw 'PokemonData.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$PokemonDataToJson(this);
    return json;
  }
}
