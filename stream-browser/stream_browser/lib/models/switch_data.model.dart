import 'package:json_annotation/json_annotation.dart';

import 'pokemon.model.dart';

part 'switch_data.model.g.dart';

@JsonSerializable(explicitToJson: true)
class SwitchData {
  List<PokemonData> pokemon;

  SwitchData({
    required this.pokemon,
  });

  factory SwitchData.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('SwitchData: json was null');
    try {
      return _$SwitchDataFromJson(json);
    } catch (e, stack) {
      throw 'SwitchData.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$SwitchDataToJson(this);
    return json;
  }
}
