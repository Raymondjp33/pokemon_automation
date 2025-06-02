import 'package:json_annotation/json_annotation.dart';

import 'catch.model.dart';

part 'pokemon.model.g.dart';

@JsonSerializable(explicitToJson: true)
class PokemonModel {
  String? name;
  @JsonKey(name: 'encounters_total')
  int? totalEncounters;
  @JsonKey(name: 'started_hunt_ts')
  num? startedHuntTimestamp;

  List<CatchModel>? catches;

  PokemonModel({
    this.name,
    this.totalEncounters,
    this.startedHuntTimestamp,
    this.catches,
  });

  static PokemonModel get emptyPokemon => PokemonModel();

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
