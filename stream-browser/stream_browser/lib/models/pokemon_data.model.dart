import 'package:json_annotation/json_annotation.dart';

import 'pokemon.model.dart';

part 'pokemon_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class PokemonData {
  List<PokemonModel> pokemon;

  PokemonData({
    required this.pokemon,
  });

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
